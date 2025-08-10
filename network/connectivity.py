from __future__ import annotations

import asyncio
import socket
import time
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any

import aiohttp
from aiohttp import ClientConnectorError

# Set up logging
logger = logging.getLogger(__name__)

try:
    # Prefer real endpoints from pyinjective if available
    from pyinjective.core.network import Network
except Exception:  # pragma: no cover - optional import safety
    Network = None  # type: ignore


@dataclass
class EndpointStatus:
    name: str
    kind: str  # http | tcp
    target: str  # URL for http, host:port for tcp
    reachable: bool
    latency_ms: Optional[float]
    error: Optional[str]
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # round latency for readability
        if d.get("latency_ms") is not None:
            d["latency_ms"] = round(float(d["latency_ms"]), 2)
        return d


class ConnectivityRegistry:
    _instance: Optional["ConnectivityRegistry"] = None

    def __init__(self) -> None:
        self._results: Dict[str, Dict[str, EndpointStatus]] = {}
        self._last_check_time: Dict[str, float] = {}
        self._check_interval: float = 300.0  # 5分钟检查间隔
        self._max_cache_age: float = 1800.0  # 30分钟最大缓存时间

    @classmethod
    def instance(cls) -> "ConnectivityRegistry":
        if cls._instance is None:
            cls._instance = ConnectivityRegistry()
        return cls._instance

    def set_results(self, env: str, results: Dict[str, EndpointStatus]) -> None:
        """设置连接性检测结果并记录时间戳"""
        self._results[env] = results
        self._last_check_time[env] = time.time()
        logger.info(f"Updated connectivity results for {env}: {len(results)} endpoints")

    def get_results(self, env: str) -> Dict[str, EndpointStatus]:
        """获取连接性检测结果，如果缓存过期则返回空字典"""
        if env not in self._results:
            return {}
        
        # 检查缓存是否过期
        if env in self._last_check_time:
            cache_age = time.time() - self._last_check_time[env]
            if cache_age > self._max_cache_age:
                logger.info(f"Cache expired for {env} (age: {cache_age:.1f}s), clearing...")
                self.clear_environment_cache(env)
                return {}
        
        return self._results[env]
    
    def is_cache_valid(self, env: str) -> bool:
        """检查指定环境的缓存是否有效"""
        if env not in self._results or env not in self._last_check_time:
            return False
        
        cache_age = time.time() - self._last_check_time[env]
        return cache_age <= self._max_cache_age
    
    def should_recheck(self, env: str) -> bool:
        """检查是否应该重新检测指定环境"""
        if env not in self._last_check_time:
            return True
        
        time_since_last_check = time.time() - self._last_check_time[env]
        return time_since_last_check >= self._check_interval
    
    def clear_cache(self) -> None:
        """清除所有缓存的连接性检测结果"""
        self._results.clear()
        self._last_check_time.clear()
        logger.info("Cleared all connectivity cache")
    
    def clear_environment_cache(self, env: str) -> None:
        """清除指定环境的缓存"""
        if env in self._results:
            del self._results[env]
        if env in self._last_check_time:
            del self._last_check_time[env]
        logger.info(f"Cleared cache for {env}")
    
    def get_cache_info(self, env: str) -> Dict[str, Any]:
        """获取缓存信息"""
        if env not in self._last_check_time:
            return {"cached": False, "age": None, "valid": False}
        
        age = time.time() - self._last_check_time[env]
        return {
            "cached": True,
            "age": age,
            "valid": self.is_cache_valid(env),
            "should_recheck": self.should_recheck(env)
        }


def _parse_host_port(address: str) -> Tuple[str, int]:
    if ":" in address:
        host, port_str = address.split(":", 1)
        try:
            return host, int(port_str)
        except ValueError:
            return address, 443
    return address, 443


def build_injective_endpoints(environment: str = "testnet") -> Dict[str, Tuple[str, str]]:
    """Return mapping: name -> (kind, target)

    kind: http|tcp; target: url or host:port
    """
    env = (environment or "testnet").lower()
    endpoints: Dict[str, Tuple[str, str]] = {}

    # 强制使用可靠的旧格式端点，因为新格式端点不可用
    if env == "testnet":
        endpoints["lcd"] = ("http", "https://testnet.lcd.injective.network")
        endpoints["grpc"] = ("tcp", "testnet.grpc.injective.network:443")
    else:
        endpoints["lcd"] = ("http", "https://lcd.injective.network")
        endpoints["grpc"] = ("tcp", "grpc.injective.network:443")

    return endpoints


async def _check_http(url: str, timeout: float = 10.0) -> Tuple[bool, Optional[float], Optional[str]]:
    start = time.perf_counter()
    try:
        async with aiohttp.ClientSession() as session:
            # Add headers to make the request more robust
            headers = {
                "User-Agent": "Injective-Agent/1.0",
                "Accept": "application/json, text/plain, */*"
            }
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout), headers=headers) as resp:
                # Consider any response as successful (even 404, 403, etc.) as it means the endpoint is reachable
                ok = resp.status < 500
                # For LCD endpoints, we might want to check if it's actually responding
                if "lcd" in url.lower() and resp.status in [404, 501]:
                    # 404 is common for LCD endpoints when the specific path doesn't exist
                    # 501 (Not Implemented) means the endpoint is reachable but doesn't support the method
                    # but the endpoint itself is reachable
                    ok = True
                # For Tendermint RPC endpoints, 405 (Method Not Allowed) is common for GET requests
                if "tm" in url.lower() and resp.status == 405:
                    # 405 means the endpoint is reachable but doesn't accept GET requests
                    ok = True
        latency = (time.perf_counter() - start) * 1000.0
        return ok, latency, None
    except asyncio.TimeoutError:
        latency = (time.perf_counter() - start) * 1000.0
        return False, latency, "Timeout"
    except aiohttp.ClientConnectorError as e:
        latency = (time.perf_counter() - start) * 1000.0
        return False, latency, f"Connection error: {str(e)}"
    except Exception as e:
        latency = (time.perf_counter() - start) * 1000.0
        return False, latency, str(e)


async def _check_tcp(address: str, timeout: float = 5.0) -> Tuple[bool, Optional[float], Optional[str]]:
    host, port = _parse_host_port(address)
    start = time.perf_counter()
    try:
        loop = asyncio.get_event_loop()
        fut = loop.getaddrinfo(host, port)
        await asyncio.wait_for(fut, timeout=timeout)
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=timeout)
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        latency = (time.perf_counter() - start) * 1000.0
        return True, latency, None
    except Exception as e:
        latency = (time.perf_counter() - start) * 1000.0
        return False, latency, str(e)


async def check_injective_connectivity(environment: str = "testnet", timeout: float = 15.0) -> Dict[str, EndpointStatus]:
    endpoints = build_injective_endpoints(environment)
    tasks: List[asyncio.Task] = []
    results: Dict[str, EndpointStatus] = {}

    async def run_check(name: str, kind: str, target: str):
        if kind == "http":
            ok, latency, err = await _check_http(target, timeout)
        else:
            ok, latency, err = await _check_tcp(target, timeout)
        results[name] = EndpointStatus(
            name=name,
            kind=kind,
            target=target,
            reachable=bool(ok),
            latency_ms=float(latency) if latency is not None else None,
            error=str(err) if err else None,
            timestamp=time.time(),
        )

    for name, (kind, target) in endpoints.items():
        tasks.append(asyncio.create_task(run_check(name, kind, target)))
    if tasks:
        await asyncio.gather(*tasks)

    # store globally
    ConnectivityRegistry.instance().set_results(environment, results)
    return results


def check_injective_connectivity_sync(environment: str = "testnet", timeout: float = 5.0) -> Dict[str, Dict[str, Any]]:
    """同步版本的连通性检测，适用于非异步环境"""
    try:
        # 尝试获取现有事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果循环正在运行，创建一个新线程来运行异步函数
                import threading
                import queue
                
                result_queue = queue.Queue()
                
                def run_async():
                    try:
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        result = new_loop.run_until_complete(check_injective_connectivity(environment, timeout=timeout))
                        result_queue.put(result)
                    except Exception as e:
                        result_queue.put({"error": str(e)})
                    finally:
                        new_loop.close()
                
                thread = threading.Thread(target=run_async)
                thread.start()
                thread.join(timeout=timeout + 5)  # 给额外5秒时间
                
                if thread.is_alive():
                    return {"error": "Timeout waiting for connectivity check"}
                
                result = result_queue.get_nowait()
                if "error" in result:
                    return {"error": result["error"]}
                
                # 转换为字典格式
                return {name: status.to_dict() for name, status in result.items()}
            else:
                # 循环未运行，可以直接使用
                return {name: status.to_dict() for name, status in 
                        loop.run_until_complete(check_injective_connectivity(environment, timeout=timeout)).items()}
        except RuntimeError:
            # 没有事件循环，创建新的
            return {name: status.to_dict() for name, status in 
                    asyncio.run(check_injective_connectivity(environment, timeout=timeout)).items()}
    except Exception as e:
        return {"error": f"Connectivity check failed: {str(e)}"}


# 全局变量：保存最佳的可用端点
_BEST_ENDPOINTS = {}

def get_best_endpoints(environment: str = "testnet") -> Dict[str, str]:
    """
    获取指定环境的最佳可用端点
    
    Args:
        environment: 环境名称 ("testnet" 或 "mainnet")
        
    Returns:
        包含最佳端点的字典，格式: {endpoint_type: endpoint_url}
    """
    global _BEST_ENDPOINTS
    
    # 检查ConnectivityRegistry中的缓存结果
    registry = ConnectivityRegistry.instance()
    cached_results = registry.get_results(environment)
    
    # 如果有有效的缓存结果，使用缓存
    if cached_results and registry.is_cache_valid(environment):
        logger.info(f"Using cached connectivity results for {environment}")
        available_endpoints = {}
        for name, status in cached_results.items():
            if status.reachable:
                available_endpoints[name] = status.target
        
        if available_endpoints:
            _BEST_ENDPOINTS[environment] = available_endpoints
            return available_endpoints
    
    # 如果没有缓存或缓存过期，进行新的检测
    logger.info(f"Running fresh connectivity check for {environment}")
    try:
        # 使用同步版本进行检测
        results = check_injective_connectivity_sync(environment, timeout=15.0)
        
        if "error" not in results:
            # 筛选出可用的端点
            available_endpoints = {}
            for name, status in results.items():
                if status.get('reachable', False):
                    available_endpoints[name] = status['target']
            
            if available_endpoints:
                _BEST_ENDPOINTS[environment] = available_endpoints
                logger.info(f"Found {len(available_endpoints)} available endpoints for {environment}")
                return available_endpoints
            else:
                logger.warning(f"No reachable endpoints found for {environment}")
        else:
            logger.warning(f"Connectivity check failed for {environment}: {results['error']}")
    except Exception as e:
        logger.error(f"Exception during connectivity check for {environment}: {e}")
    
    # 如果检测失败或没有可用端点，使用默认端点
    default_endpoints = _get_default_endpoints(environment)
    logger.info(f"Using default endpoints for {environment}")
    _BEST_ENDPOINTS[environment] = default_endpoints
    return default_endpoints

def _get_default_endpoints(environment: str) -> Dict[str, str]:
    """获取默认端点作为fallback"""
    if environment.lower() == "testnet":
        return {
            "lcd": "https://testnet.lcd.injective.network",
            "grpc": "testnet.grpc.injective.network:9900"
        }
    else:
        return {
            "lcd": "https://lcd.injective.network",
            "grpc": "grpc.injective.network:9900"
        }

def refresh_endpoints(environment: str = "testnet") -> Dict[str, str]:
    """
    刷新指定环境的端点检测结果
    
    Args:
        environment: 环境名称
        
    Returns:
        更新后的最佳端点
    """
    global _BEST_ENDPOINTS
    
    logger.info(f"Force refreshing endpoints for {environment}")
    
    # 清除ConnectivityRegistry缓存
    registry = ConnectivityRegistry.instance()
    registry.clear_environment_cache(environment)
    
    # 清除本地缓存
    if environment in _BEST_ENDPOINTS:
        del _BEST_ENDPOINTS[environment]
    
    # 重新检测
    return get_best_endpoints(environment)

def get_endpoint_status_summary(environment: str = "testnet") -> str:
    """
    获取端点状态摘要
    
    Args:
        environment: 环境名称
        
    Returns:
        格式化的状态摘要字符串
    """
    try:
        results = check_injective_connectivity_sync(environment, timeout=15.0)
        
        if "error" in results:
            return f"❌ 端点检测失败: {results['error']}"
        
        summary = f"🌐 {environment.upper()} 网络端点状态:\n"
        total = len(results)
        available = sum(1 for r in results.values() if r.get('reachable', False))
        
        summary += f"   总体状态: {available}/{total} 个端点可用\n"
        
        for name, status in results.items():
            icon = "✅" if status.get('reachable', False) else "❌"
            latency = f"{status['latency_ms']:.0f}ms" if status.get('latency_ms') else "N/A"
            summary += f"   {icon} {name}: {status['target']} (延迟: {latency})\n"
        
        return summary
        
    except Exception as e:
        return f"❌ 端点状态检测异常: {str(e)}"


async def validate_endpoint_availability(environment: str, endpoint_type: str, endpoint_url: str, timeout: float = 5.0) -> bool:
    """
    验证指定端点的可用性，如果不可用则自动重新测试
    
    Args:
        environment: 环境名称
        endpoint_type: 端点类型 ("lcd", "grpc", "tendermint_rpc")
        endpoint_url: 端点URL
        timeout: 超时时间
        
    Returns:
        端点是否可用
    """
    logger.info(f"Validating {endpoint_type} endpoint availability: {endpoint_url}")
    
    try:
        # 尝试连接端点
        if endpoint_type == "lcd" or "http" in endpoint_url.lower():
            # HTTP端点测试
            ok, latency, error = await _check_http(endpoint_url, timeout)
        else:
            # TCP端点测试
            ok, latency, error = await _check_tcp(endpoint_url, timeout)
        
        if ok:
            logger.info(f"✅ {endpoint_type} endpoint is available: {endpoint_url} (latency: {latency:.1f}ms)")
            return True
        else:
            logger.warning(f"❌ {endpoint_type} endpoint is not available: {endpoint_url} (error: {error})")
            
            # 端点不可用，清除缓存并重新测试
            logger.info(f"Clearing cache and re-running connectivity test for {environment}")
            registry = ConnectivityRegistry.instance()
            registry.clear_environment_cache(environment)
            
            # 重新运行连接性测试
            new_results = await check_injective_connectivity(environment, timeout=timeout)
            
            # 检查是否有新的可用端点
            for name, status in new_results.items():
                if name == endpoint_type and status.reachable:
                    logger.info(f"Found new available {endpoint_type} endpoint: {status.target}")
                    return True
            
            logger.warning(f"No new available {endpoint_type} endpoint found for {environment}")
            return False
            
    except Exception as e:
        logger.error(f"Error validating {endpoint_type} endpoint {endpoint_url}: {e}")
        
        # 发生异常时也清除缓存并重新测试
        logger.info(f"Exception occurred, clearing cache and re-running connectivity test for {environment}")
        registry = ConnectivityRegistry.instance()
        registry.clear_environment_cache(environment)
        
        try:
            new_results = await check_injective_connectivity(environment, timeout=timeout)
            for name, status in new_results.items():
                if name == endpoint_type and status.reachable:
                    logger.info(f"Found new available {endpoint_type} endpoint after exception: {status.target}")
                    return True
        except Exception as retry_error:
            logger.error(f"Retry connectivity test failed: {retry_error}")
        
        return False


def get_smart_endpoint(environment: str, endpoint_type: str, force_refresh: bool = False) -> str:
    """
    智能获取端点，优先使用缓存结果，必要时自动刷新
    
    Args:
        environment: 环境名称
        endpoint_type: 端点类型
        force_refresh: 是否强制刷新
        
    Returns:
        最佳可用端点URL
    """
    if force_refresh:
        logger.info(f"Force refreshing endpoints for {environment}")
        refresh_endpoints(environment)
    
    # 获取最佳端点
    best_endpoints = get_best_endpoints(environment)
    
    if endpoint_type in best_endpoints:
        endpoint_url = best_endpoints[endpoint_type]
        logger.info(f"Using {endpoint_type} endpoint from cache: {endpoint_url}")
        return endpoint_url
    
    # 如果没有找到指定类型的端点，使用默认端点
    default_endpoints = _get_default_endpoints(environment)
    if endpoint_type in default_endpoints:
        logger.warning(f"No {endpoint_type} endpoint found in cache, using default: {default_endpoints[endpoint_type]}")
        return default_endpoints[endpoint_type]
    
    # 最后的fallback
    logger.error(f"No {endpoint_type} endpoint available for {environment}")
    if environment.lower() == "testnet":
        return "https://testnet.lcd.injective.network"
    else:
        return "https://lcd.injective.network"


