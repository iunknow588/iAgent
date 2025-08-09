#!/usr/bin/env python3
"""
服务器状态检查脚本 - Injective Agent API
检查服务器运行状态和连接问题
"""

import asyncio
import aiohttp
import json
import subprocess
import psutil
import socket
from datetime import datetime

class ServerStatusChecker:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def check_port_usage(self, port=5000):
        """检查端口使用情况"""
        print(f"🔍 检查端口 {port} 使用情况...")
        
        try:
            # 检查端口是否被占用
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"   ✅ 端口 {port} 正在被使用")
                return True
            else:
                print(f"   ❌ 端口 {port} 未被使用")
                return False
        except Exception as e:
            print(f"   ❌ 端口检查失败: {e}")
            return False
    
    def check_process_status(self):
        """检查Python进程状态"""
        print("🔍 检查Python进程...")
        
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python3' or proc.info['name'] == 'python':
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if 'agent_server.py' in cmdline or 'quick_start' in cmdline:
                        python_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if python_processes:
            print(f"   ✅ 找到 {len(python_processes)} 个相关Python进程:")
            for proc in python_processes:
                print(f"      PID: {proc['pid']}, 命令: {proc['cmdline'][:100]}...")
            return True
        else:
            print("   ❌ 未找到相关的Python进程")
            return False
    
    async def test_server_endpoints(self):
        """测试服务器端点"""
        print("🔍 测试服务器端点...")
        
        endpoints = [
            ("/", "根端点"),
            ("/ping", "健康检查"),
            ("/history", "历史记录")
        ]
        
        results = []
        for endpoint, description in endpoints:
            try:
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    if response.status == 200:
                        print(f"   ✅ {description} ({endpoint}): 正常")
                        results.append(True)
                    else:
                        print(f"   ❌ {description} ({endpoint}): HTTP {response.status}")
                        results.append(False)
            except Exception as e:
                print(f"   ❌ {description} ({endpoint}): 连接失败 - {e}")
                results.append(False)
        
        return all(results)
    
    async def test_chat_endpoint(self):
        """测试聊天端点"""
        print("🔍 测试聊天端点...")
        
        test_data = {
            "message": "Hello, this is a test message",
            "session_id": "test_session",
            "agent_id": "test_agent",
            "agent_key": "default",
            "environment": "testnet"
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/chat",
                json=test_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ 聊天端点: 正常")
                    print(f"      响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    return True
                else:
                    print(f"   ❌ 聊天端点: HTTP {response.status}")
                    return False
        except Exception as e:
            print(f"   ❌ 聊天端点: 连接失败 - {e}")
            return False
    
    def suggest_fixes(self, port_ok, process_ok, endpoints_ok, chat_ok):
        """根据检查结果提供修复建议"""
        print("\n🔧 修复建议:")
        
        if not port_ok:
            print("   1. 启动服务器:")
            print("      python3 quick_start_service.py --start")
            print("      或者")
            print("      python3 agent_server.py")
        
        if not process_ok:
            print("   2. 检查服务器进程:")
            print("      ps aux | grep python")
            print("      如果进程不存在，重新启动服务器")
        
        if not endpoints_ok or not chat_ok:
            print("   3. 检查服务器日志:")
            print("      查看 server.log 文件了解错误详情")
            print("   4. 重启服务器:")
            print("      python3 quick_start_service.py --stop")
            print("      python3 quick_start_service.py --start")
        
        print("   5. 检查环境配置:")
        print("      确保 .env 文件存在且包含 OPENAI_API_KEY")
        print("   6. 修复依赖问题:")
        print("      python3 fix_dependencies.py")
    
    async def run_full_check(self):
        """运行完整的状态检查"""
        print("=" * 60)
        print("🔍 Injective Agent API 服务器状态检查")
        print("=" * 60)
        
        # 检查端口
        port_ok = self.check_port_usage()
        
        # 检查进程
        process_ok = self.check_process_status()
        
        # 测试端点
        endpoints_ok = await self.test_server_endpoints()
        
        # 测试聊天功能
        chat_ok = await self.test_chat_endpoint()
        
        # 总结
        print("\n📊 检查总结:")
        print(f"   端口状态: {'✅ 正常' if port_ok else '❌ 异常'}")
        print(f"   进程状态: {'✅ 正常' if process_ok else '❌ 异常'}")
        print(f"   端点状态: {'✅ 正常' if endpoints_ok else '❌ 异常'}")
        print(f"   聊天功能: {'✅ 正常' if chat_ok else '❌ 异常'}")
        
        overall_status = port_ok and process_ok and endpoints_ok and chat_ok
        print(f"\n总体状态: {'✅ 服务器运行正常' if overall_status else '❌ 服务器存在问题'}")
        
        if not overall_status:
            self.suggest_fixes(port_ok, process_ok, endpoints_ok, chat_ok)
        
        return overall_status

async def main():
    """主函数"""
    async with ServerStatusChecker() as checker:
        return await checker.run_full_check()

if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
