#!/usr/bin/env python3
"""
自动化部署和启动脚本 - Injective Agent API
自动检查环境、安装依赖、启动服务器并运行测试
"""

import os
import sys
import subprocess
import time
import asyncio
import aiohttp
import json
from datetime import datetime

class AutoDeployer:
    def __init__(self):
        self.server_process = None
        self.base_url = "http://localhost:5000"
        
    def check_python_version(self):
        """检查Python版本"""
        print("🐍 检查Python版本...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"❌ Python版本过低: {version.major}.{version.minor}")
            print("   需要Python 3.8或更高版本")
            return False
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    
    def check_dependencies(self):
        """检查依赖"""
        print("\n📦 检查依赖...")
        required_packages = [
            "openai",
            "quart",
            "hypercorn",
            "aiohttp",
            "psutil",
            "python-dotenv"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                print(f"✅ {package}")
            except ImportError:
                print(f"❌ {package} - 未安装")
                missing_packages.append(package)
        
        if missing_packages:
            print(f"\n📥 安装缺失的依赖: {', '.join(missing_packages)}")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install"
                ] + missing_packages)
                print("✅ 依赖安装完成")
            except subprocess.CalledProcessError as e:
                print(f"❌ 依赖安装失败: {e}")
                return False
        
        return True
    
    def check_environment(self):
        """检查环境变量"""
        print("\n🔧 检查环境变量...")
        
        # 检查.env文件
        if not os.path.exists(".env"):
            print("⚠️  未找到.env文件")
            print("   请创建.env文件并设置OPENAI_API_KEY")
            return False
        
        # 检查API密钥
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("❌ 未设置OPENAI_API_KEY环境变量")
                return False
            print("✅ 环境变量配置正确")
            return True
        except Exception as e:
            print(f"❌ 环境变量检查失败: {e}")
            return False
    
    def start_server(self):
        """启动服务器"""
        print("\n🚀 启动Agent服务器...")
        
        try:
            # 检查端口是否被占用
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 5000))
            sock.close()
            
            if result == 0:
                print("⚠️  端口5000已被占用")
                print("   请停止其他服务或使用不同端口")
                return False
            
            # 启动服务器
            self.server_process = subprocess.Popen([
                sys.executable, "agent_server.py", "--port", "5000"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待服务器启动
            print("⏳ 等待服务器启动...")
            time.sleep(3)
            
            # 检查服务器是否启动成功
            if self.server_process.poll() is None:
                print("✅ 服务器启动成功")
                return True
            else:
                print("❌ 服务器启动失败")
                return False
                
        except Exception as e:
            print(f"❌ 启动服务器时出错: {e}")
            return False
    
    async def test_server(self):
        """测试服务器"""
        print("\n🧪 测试服务器...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # 测试健康检查
                async with session.get(f"{self.base_url}/ping") as response:
                    if response.status == 200:
                        data = await response.json()
                        print("✅ 服务器健康检查通过")
                        return True
                    else:
                        print(f"❌ 服务器健康检查失败: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ 服务器测试失败: {e}")
            return False
    
    async def run_quick_tests(self):
        """运行快速测试"""
        print("\n⚡ 运行快速测试...")
        
        tests = [
            ("基础聊天", "你好，请介绍一下你自己"),
            ("功能查询", "你能帮我做什么？"),
            ("区块链咨询", "请告诉我Injective的特点")
        ]
        
        results = []
        async with aiohttp.ClientSession() as session:
            for test_name, message in tests:
                try:
                    start_time = time.time()
                    async with session.post(
                        f"{self.base_url}/chat",
                        json={
                            "message": message,
                            "session_id": f"deploy_test_{test_name}",
                            "agent_id": f"deploy_agent_{test_name}",
                            "agent_key": "default",
                            "environment": "testnet"
                        }
                    ) as response:
                        response_time = time.time() - start_time
                        if response.status == 200:
                            print(f"✅ {test_name}: {response_time:.2f}s")
                            results.append(True)
                        else:
                            print(f"❌ {test_name}: HTTP {response.status}")
                            results.append(False)
                except Exception as e:
                    print(f"❌ {test_name}: {e}")
                    results.append(False)
        
        success_rate = (sum(results) / len(results)) * 100
        print(f"\n📊 快速测试结果: {sum(results)}/{len(results)} 通过 ({success_rate:.1f}%)")
        return all(results)
    
    def stop_server(self):
        """停止服务器"""
        if self.server_process:
            print("\n🛑 停止服务器...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                print("✅ 服务器已停止")
            except subprocess.TimeoutExpired:
                print("⚠️  服务器强制终止")
                self.server_process.kill()
    
    def generate_deployment_report(self, success):
        """生成部署报告"""
        report = {
            "deployment_time": datetime.now().isoformat(),
            "success": success,
            "server_url": self.base_url,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform
        }
        
        with open("deployment_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 部署报告已保存到: deployment_report.json")
    
    async def deploy(self):
        """执行完整部署流程"""
        print("🤖 Injective Agent API 自动化部署")
        print("=" * 50)
        
        steps = [
            ("检查Python版本", self.check_python_version),
            ("检查依赖", self.check_dependencies),
            ("检查环境变量", self.check_environment),
            ("启动服务器", self.start_server),
            ("测试服务器", self.test_server),
            ("运行快速测试", self.run_quick_tests)
        ]
        
        success = True
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            
            if asyncio.iscoroutinefunction(step_func):
                result = await step_func()
            else:
                result = step_func()
            
            if not result:
                print(f"❌ {step_name}失败")
                success = False
                break
            else:
                print(f"✅ {step_name}成功")
        
        # 生成部署报告
        self.generate_deployment_report(success)
        
        if success:
            print("\n🎉 部署成功！")
            print(f"🔗 服务器地址: {self.base_url}")
            print("📋 可用端点:")
            print("   GET  /     - API信息")
            print("   GET  /ping - 健康检查")
            print("   POST /chat - 聊天功能")
            print("   GET  /history - 历史记录")
            print("   POST /clear - 清除历史")
            print("\n按 Ctrl+C 停止服务器")
            
            # 保持服务器运行
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                pass
        else:
            print("\n❌ 部署失败，请检查错误信息")
        
        # 清理
        self.stop_server()

async def main():
    """主函数"""
    deployer = AutoDeployer()
    await deployer.deploy()

if __name__ == "__main__":
    asyncio.run(main())
