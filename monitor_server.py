#!/usr/bin/env python3
"""
服务器性能监控脚本 - Injective Agent API
实时监控服务器状态和性能
"""

import asyncio
import aiohttp
import json
import time
import psutil
import os
from datetime import datetime
from collections import deque

class ServerMonitor:
    def __init__(self, base_url="http://localhost:5000", interval=5):
        self.base_url = base_url
        self.interval = interval
        self.session = None
        self.response_times = deque(maxlen=100)
        self.error_count = 0
        self.success_count = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_system_info(self):
        """获取系统信息"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_gb": memory.used / (1024**3),
            "memory_total_gb": memory.total / (1024**3),
            "disk_percent": disk.percent,
            "disk_used_gb": disk.used / (1024**3),
            "disk_total_gb": disk.total / (1024**3)
        }
    
    async def test_server_health(self):
        """测试服务器健康状态"""
        start_time = time.time()
        try:
            async with self.session.get(f"{self.base_url}/ping") as response:
                response_time = time.time() - start_time
                self.response_times.append(response_time)
                
                if response.status == 200:
                    self.success_count += 1
                    data = await response.json()
                    return {
                        "status": "healthy",
                        "response_time": response_time,
                        "status_code": response.status,
                        "data": data
                    }
                else:
                    self.error_count += 1
                    return {
                        "status": "error",
                        "response_time": response_time,
                        "status_code": response.status,
                        "error": f"HTTP {response.status}"
                    }
        except Exception as e:
            self.error_count += 1
            return {
                "status": "error",
                "response_time": time.time() - start_time,
                "error": str(e)
            }
    
    async def test_chat_endpoint(self):
        """测试聊天端点性能"""
        start_time = time.time()
        try:
            async with self.session.post(
                f"{self.base_url}/chat",
                json={
                    "message": "ping",
                    "session_id": "monitor_session",
                    "agent_id": "monitor_agent",
                    "agent_key": "default",
                    "environment": "testnet"
                }
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "success",
                        "response_time": response_time,
                        "status_code": response.status
                    }
                else:
                    return {
                        "status": "error",
                        "response_time": response_time,
                        "status_code": response.status
                    }
        except Exception as e:
            return {
                "status": "error",
                "response_time": time.time() - start_time,
                "error": str(e)
            }
    
    def calculate_stats(self):
        """计算统计信息"""
        if not self.response_times:
            return {}
        
        times = list(self.response_times)
        return {
            "avg_response_time": sum(times) / len(times),
            "min_response_time": min(times),
            "max_response_time": max(times),
            "total_requests": self.success_count + self.error_count,
            "success_rate": (self.success_count / (self.success_count + self.error_count)) * 100 if (self.success_count + self.error_count) > 0 else 0
        }
    
    def print_status(self, health_result, chat_result, system_info, stats):
        """打印状态信息"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🤖 Injective Agent API 服务器监控")
        print("=" * 60)
        print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 服务器: {self.base_url}")
        print(f"⏱️  监控间隔: {self.interval}秒")
        print("=" * 60)
        
        # 服务器状态
        print("📊 服务器状态:")
        print(f"   健康检查: {'✅ 正常' if health_result['status'] == 'healthy' else '❌ 异常'}")
        print(f"   响应时间: {health_result['response_time']:.3f}s")
        print(f"   聊天端点: {'✅ 正常' if chat_result['status'] == 'success' else '❌ 异常'}")
        print(f"   聊天响应: {chat_result['response_time']:.3f}s")
        
        # 系统资源
        print("\n💻 系统资源:")
        print(f"   CPU使用率: {system_info['cpu_percent']:.1f}%")
        print(f"   内存使用率: {system_info['memory_percent']:.1f}%")
        print(f"   内存使用: {system_info['memory_used_gb']:.2f}GB / {system_info['memory_total_gb']:.2f}GB")
        print(f"   磁盘使用率: {system_info['disk_percent']:.1f}%")
        print(f"   磁盘使用: {system_info['disk_used_gb']:.2f}GB / {system_info['disk_total_gb']:.2f}GB")
        
        # 性能统计
        if stats:
            print("\n📈 性能统计:")
            print(f"   平均响应时间: {stats['avg_response_time']:.3f}s")
            print(f"   最快响应时间: {stats['min_response_time']:.3f}s")
            print(f"   最慢响应时间: {stats['max_response_time']:.3f}s")
            print(f"   总请求数: {stats['total_requests']}")
            print(f"   成功率: {stats['success_rate']:.1f}%")
        
        print("\n" + "=" * 60)
        print("按 Ctrl+C 停止监控")
    
    async def monitor(self):
        """开始监控"""
        print("🚀 开始监控 Injective Agent API 服务器...")
        print("=" * 60)
        
        try:
            while True:
                # 获取系统信息
                system_info = self.get_system_info()
                
                # 测试服务器健康状态
                health_result = await self.test_server_health()
                
                # 测试聊天端点
                chat_result = await self.test_chat_endpoint()
                
                # 计算统计信息
                stats = self.calculate_stats()
                
                # 打印状态
                self.print_status(health_result, chat_result, system_info, stats)
                
                # 等待下次监控
                await asyncio.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 监控已停止")
            print(f"📊 最终统计:")
            stats = self.calculate_stats()
            if stats:
                print(f"   总请求数: {stats['total_requests']}")
                print(f"   成功率: {stats['success_rate']:.1f}%")
                print(f"   平均响应时间: {stats['avg_response_time']:.3f}s")

async def main():
    """主函数"""
    print("🔍 Injective Agent API 服务器监控工具")
    print("=" * 50)
    
    # 检查依赖
    try:
        import psutil
    except ImportError:
        print("❌ 缺少依赖: psutil")
        print("请运行: pip install psutil")
        return
    
    async with ServerMonitor() as monitor:
        await monitor.monitor()

if __name__ == "__main__":
    asyncio.run(main())
