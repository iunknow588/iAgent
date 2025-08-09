#!/usr/bin/env python3
"""
服务器状态监控脚本 - Injective Agent API
实时显示服务器状态和日志信息
"""

import asyncio
import aiohttp
import json
import time
import os
import psutil
from datetime import datetime
from collections import deque

class ServerStatusMonitor:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = None
        self.status_history = deque(maxlen=50)
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_system_info(self):
        """获取系统信息"""
        try:
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
        except:
            return {}
    
    def get_process_info(self):
        """获取进程信息"""
        try:
            # 查找Python进程
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                        if 'agent_server.py' in cmdline:
                            python_processes.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cpu_percent': proc.info['cpu_percent'],
                                'memory_percent': proc.info['memory_percent'],
                                'cmdline': cmdline
                            })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return python_processes
        except:
            return []
    
    async def check_server_health(self):
        """检查服务器健康状态"""
        try:
            start_time = time.time()
            async with self.session.get(f"{self.base_url}/ping", timeout=5) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "healthy",
                        "response_time": response_time,
                        "status_code": response.status,
                        "timestamp": data.get("timestamp", ""),
                        "version": data.get("version", "")
                    }
                else:
                    return {
                        "status": "error",
                        "response_time": response_time,
                        "status_code": response.status,
                        "error": f"HTTP {response.status}"
                    }
        except Exception as e:
            return {
                "status": "error",
                "response_time": 0,
                "error": str(e)
            }
    
    async def test_chat_endpoint(self):
        """测试聊天端点"""
        try:
            start_time = time.time()
            async with self.session.post(
                f"{self.base_url}/chat",
                json={
                    "message": "status check",
                    "session_id": "status_monitor",
                    "agent_id": "status_agent",
                    "agent_key": "default",
                    "environment": "testnet"
                },
                timeout=10
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "success",
                        "response_time": response_time,
                        "status_code": response.status,
                        "has_function_call": data.get("function_call") is not None
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
                "response_time": 0,
                "error": str(e)
            }
    
    def clear_screen(self):
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_status(self, health_result, chat_result, system_info, process_info):
        """打印状态信息"""
        self.clear_screen()
        
        print("🤖 Injective Agent API 服务器状态监控")
        print("=" * 60)
        print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 服务器: {self.base_url}")
        print("=" * 60)
        
        # 服务器状态
        print("📊 服务器状态:")
        health_status = "✅ 正常" if health_result["status"] == "healthy" else "❌ 异常"
        print(f"   健康检查: {health_status}")
        print(f"   响应时间: {health_result['response_time']:.3f}s")
        print(f"   版本: {health_result.get('version', 'N/A')}")
        
        chat_status = "✅ 正常" if chat_result["status"] == "success" else "❌ 异常"
        print(f"   聊天端点: {chat_status}")
        print(f"   聊天响应: {chat_result['response_time']:.3f}s")
        
        # 进程信息
        if process_info:
            print("\n🖥️  进程信息:")
            for proc in process_info:
                print(f"   PID: {proc['pid']}")
                print(f"   CPU: {proc['cpu_percent']:.1f}%")
                print(f"   内存: {proc['memory_percent']:.1f}%")
                print(f"   命令: {proc['cmdline'][:50]}...")
        else:
            print("\n🖥️  进程信息: 未找到agent_server.py进程")
        
        # 系统资源
        if system_info:
            print("\n💻 系统资源:")
            print(f"   CPU使用率: {system_info['cpu_percent']:.1f}%")
            print(f"   内存使用率: {system_info['memory_percent']:.1f}%")
            print(f"   内存使用: {system_info['memory_used_gb']:.2f}GB / {system_info['memory_total_gb']:.2f}GB")
            print(f"   磁盘使用率: {system_info['disk_percent']:.1f}%")
            print(f"   磁盘使用: {system_info['disk_used_gb']:.2f}GB / {system_info['disk_total_gb']:.2f}GB")
        
        # 状态历史
        if self.status_history:
            print("\n📈 状态历史:")
            recent_statuses = list(self.status_history)[-5:]  # 最近5次
            for i, status in enumerate(recent_statuses):
                timestamp = status.get("timestamp", "")
                health = "✅" if status.get("health_status") == "healthy" else "❌"
                chat = "✅" if status.get("chat_status") == "success" else "❌"
                print(f"   {timestamp}: 健康{health} 聊天{chat}")
        
        print("\n" + "=" * 60)
        print("按 Ctrl+C 停止监控")
    
    async def monitor(self, interval=5):
        """开始监控"""
        print("🚀 开始监控 Injective Agent API 服务器...")
        print("=" * 60)
        
        try:
            while True:
                # 获取系统信息
                system_info = self.get_system_info()
                process_info = self.get_process_info()
                
                # 检查服务器健康状态
                health_result = await self.check_server_health()
                
                # 测试聊天端点
                chat_result = await self.test_chat_endpoint()
                
                # 记录状态历史
                self.status_history.append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "health_status": health_result["status"],
                    "chat_status": chat_result["status"],
                    "health_response_time": health_result.get("response_time", 0),
                    "chat_response_time": chat_result.get("response_time", 0)
                })
                
                # 打印状态
                self.print_status(health_result, chat_result, system_info, process_info)
                
                # 等待下次监控
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 监控已停止")
            print("📊 监控统计:")
            if self.status_history:
                total_checks = len(self.status_history)
                healthy_checks = sum(1 for s in self.status_history if s["health_status"] == "healthy")
                chat_success = sum(1 for s in self.status_history if s["chat_status"] == "success")
                
                print(f"   总检查次数: {total_checks}")
                print(f"   健康检查成功率: {(healthy_checks/total_checks*100):.1f}%")
                print(f"   聊天功能成功率: {(chat_success/total_checks*100):.1f}%")

async def main():
    """主函数"""
    print("🔍 Injective Agent API 服务器状态监控")
    print("=" * 50)
    
    # 检查依赖
    try:
        import psutil
    except ImportError:
        print("❌ 缺少依赖: psutil")
        print("请运行: pip install psutil")
        return
    
    async with ServerStatusMonitor() as monitor:
        await monitor.monitor()

if __name__ == "__main__":
    asyncio.run(main())
