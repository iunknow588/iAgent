#!/usr/bin/env python3
"""
服务器管理工具 - Injective Agent API
🔧 专注于服务器生命周期管理
功能：环境检查、依赖安装、服务器启动/停止、状态监控

原文件名：quick_start.py
新文件名：quick_start_service.py
"""

import asyncio
import subprocess
import sys
import time
import os
from datetime import datetime

class QuickStart:
    def __init__(self):
        self.server_process = None
        self.base_url = "http://localhost:5000"
        
    def check_dependencies(self):
        """检查依赖"""
        print("🔍 检查依赖...")
        
        # 包名和模块名的映射关系
        package_mappings = {
            "openai": "openai",
            "quart": "quart", 
            "hypercorn": "hypercorn",
            "aiohttp": "aiohttp",
            "psutil": "psutil",
            "python-dotenv": "dotenv"  # 关键修复：包名和模块名不同
        }
        
        missing_packages = []
        for package_name, module_name in package_mappings.items():
            try:
                __import__(module_name)
                print(f"   ✅ {package_name}")
            except ImportError:
                print(f"   ❌ {package_name} - 未安装")
                missing_packages.append(package_name)
        
        if missing_packages:
            print(f"\n📥 安装缺失的依赖...")
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
        """检查环境"""
        print("\n🔧 检查环境...")
        
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
            print("✅ 环境配置正确")
            return True
        except Exception as e:
            print(f"❌ 环境检查失败: {e}")
            return False
    
    def start_server(self, background=False):
        """启动服务器"""
        if background:
            print("\n🚀 启动服务器（后台模式）...")
        else:
            print("\n🚀 启动服务器...")
        
        try:
            # 检查端口是否被占用
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 5000))
            sock.close()
            
            if result == 0:
                print("⚠️  端口5000已被占用")
                print("   服务器可能已经在运行")
                return True
            
            # 启动服务器
            if background:
                # 后台启动，重定向输出到文件
                with open("server.log", "w") as log_file:
                    self.server_process = subprocess.Popen([
                        sys.executable, "agent_server.py", "--port", "5000"
                    ], stdout=log_file, stderr=log_file)
                print("📄 服务器日志: server.log")
            else:
                # 前台启动
                self.server_process = subprocess.Popen([
                    sys.executable, "agent_server.py", "--port", "5000"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待服务器启动
            print("⏳ 等待服务器启动...")
            time.sleep(5)
            
            # 检查服务器是否启动成功
            if self.server_process.poll() is None:
                if background:
                    print("✅ 服务器已在后台启动")
                    print("💡 现在可以在同一终端启动客户端了")
                else:
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
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/ping", timeout=5) as response:
                    if response.status == 200:
                        print("✅ 服务器测试通过")
                        return True
                    else:
                        print(f"❌ 服务器测试失败: HTTP {response.status}")
                        return False
        except Exception as e:
            print(f"❌ 服务器测试失败: {e}")
            return False
    
    def run_tests(self):
        """运行测试"""
        print("\n📋 运行测试...")
        
        tests = [
            ("基础API测试", "test_agent_api.py"),
            ("无私钥测试", "test_without_private_key.py"),
            ("真实私钥测试", "test_with_real_private_key.py"),
            ("综合测试报告", "generate_test_report.py")
        ]
        
        results = []
        for test_name, test_file in tests:
            print(f"   运行: {test_name}")
            try:
                result = subprocess.run([
                    sys.executable, test_file
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print(f"   ✅ {test_name} 通过")
                    results.append(True)
                else:
                    print(f"   ❌ {test_name} 失败")
                    results.append(False)
            except subprocess.TimeoutExpired:
                print(f"   ⏰ {test_name} 超时")
                results.append(False)
            except Exception as e:
                print(f"   💥 {test_name} 异常: {e}")
                results.append(False)
        
        success_count = sum(results)
        total_count = len(results)
        print(f"\n📊 测试结果: {success_count}/{total_count} 通过")
        
        return success_count >= total_count * 0.8  # 80%成功率
    
    def show_menu(self):
        """显示菜单"""
        print("\n" + "=" * 50)
        print("🔧 Injective Agent API 服务器管理")
        print("=" * 50)
        print("1. 🚀 启动服务器（后台）")
        print("2. 启动服务器（前台）")
        print("3. 停止服务器")
        print("4. 检查服务器状态")
        print("5. 检查环境和依赖")
        print("6. 退出")
        print("=" * 50)
        print("💡 提示: 这是服务器管理工具，客户端请使用 quick_start.py")
    
    async def start_monitoring(self):
        """启动监控"""
        print("\n📊 启动监控...")
        try:
            subprocess.run([
                sys.executable, "server_status.py"
            ])
        except KeyboardInterrupt:
            print("\n🛑 监控已停止")
    
    async def full_startup(self):
        """完整启动流程"""
        print("🚀 开始完整启动流程...")
        
        # 检查依赖
        if not self.check_dependencies():
            print("❌ 依赖检查失败")
            return False
        
        # 检查环境
        if not self.check_environment():
            print("❌ 环境检查失败")
            return False
        
        # 启动服务器
        if not self.start_server():
            print("❌ 服务器启动失败")
            return False
        
        # 测试服务器
        if not await self.test_server():
            print("❌ 服务器测试失败")
            return False
        
        # 运行测试
        if not self.run_tests():
            print("⚠️  部分测试失败")
        
        print("\n🎉 启动流程完成！")
        print("服务器地址: http://localhost:5000")
        print("可用端点:")
        print("  GET  /     - API信息")
        print("  GET  /ping - 健康检查")
        print("  POST /chat - 聊天功能")
        print("  GET  /history - 历史记录")
        print("  POST /clear - 清除历史")
        
        return True
    
    async def interactive_menu(self):
        """交互式菜单"""
        while True:
            self.show_menu()
            
            try:
                choice = input("\n请选择操作 (1-6) [默认:1]: ").strip().lower()
                
                # 如果用户直接按回车，默认选择1（后台服务器+客户端）
                if not choice:
                    choice = "1"
                
                # 支持多种退出方式
                if choice in ["6", "q", "quit", "exit", "退出"]:
                    print("👋 再见！")
                    break
                
                elif choice == "1":
                    # 启动服务器（后台）
                    if self.start_server(background=True):
                        print("✅ 服务器后台启动成功")
                        print("💡 服务器日志: server.log")
                        print("💡 现在可以使用 quick_start.py 启动客户端")
                        
                        # 如果服务器已经运行，提供额外选项
                        try:
                            print("\n🎯 下一步操作:")
                            print("1. 启动客户端")
                            print("2. 返回主菜单")
                            print("3. 退出")
                            next_choice = input("请选择 (1-3) [默认:1]: ").strip()
                            
                            if not next_choice or next_choice == "1":
                                # 启动客户端
                                print("\n🚀 启动客户端...")
                                client_script = os.path.join(os.path.dirname(__file__), "quick_start_client.py")
                                if os.path.exists(client_script):
                                    try:
                                        subprocess.run([sys.executable, client_script], check=True)
                                    except subprocess.CalledProcessError:
                                        print("❌ 客户端启动失败")
                                    except KeyboardInterrupt:
                                        print("\n👋 客户端已退出")
                                else:
                                    print(f"❌ 找不到客户端脚本: {client_script}")
                            elif next_choice == "3":
                                print("👋 再见！")
                                break
                            # 如果选择2或无效选择，继续显示主菜单
                        except EOFError:
                            print("\n🤖 自动化模式，返回主菜单")
                    else:
                        print("❌ 服务器启动失败")
                
                elif choice == "2":
                    # 启动服务器（前台）
                    if self.start_server(background=False):
                        print("✅ 服务器启动成功")
                        print("💡 服务器运行中，按 Ctrl+C 停止")
                        try:
                            # 等待用户中断
                            while self.server_process and self.server_process.poll() is None:
                                time.sleep(1)
                        except KeyboardInterrupt:
                            print("\n🛑 停止服务器...")
                            if self.server_process:
                                self.server_process.terminate()
                    else:
                        print("❌ 服务器启动失败")
                
                elif choice == "3":
                    # 停止服务器
                    if self.stop_server():
                        print("✅ 服务器停止成功")
                    else:
                        print("⚠️  服务器停止失败或未运行")
                
                elif choice == "4":
                    # 检查服务器状态
                    if self.check_server_status():
                        print("✅ 服务器运行正常")
                    else:
                        print("❌ 服务器未运行或状态异常")
                
                elif choice == "5":
                    # 检查环境和依赖
                    if self.check_dependencies() and self.check_environment():
                        print("✅ 环境和依赖检查通过")
                    else:
                        print("❌ 环境和依赖检查失败")
                
                else:
                    print("❌ 无效选择，请重新输入")
                
                try:
                    input("\n按回车键继续...")
                except EOFError:
                    print("\n🤖 自动化模式，退出程序")
                    break
                
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except EOFError:
                print("\n\n🤖 检测到自动化模式，退出程序")
                break
            except Exception as e:
                print(f"❌ 操作失败: {e}")
                try:
                    input("\n按回车键继续...")
                except EOFError:
                    print("\n🤖 自动化模式，退出程序")
                    break
    
    def stop_server(self):
        """停止服务器"""
        print("\n🛑 停止服务器...")
        
        # 查找并停止agent_server进程
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'python3' and any('agent_server' in cmd for cmd in proc.info['cmdline']):
                        proc.terminate()
                        print(f"✅ 已停止服务器进程 (PID: {proc.info['pid']})")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            print("⚠️  未找到运行中的服务器进程")
            return False
        except Exception as e:
            print(f"❌ 停止服务器失败: {e}")
            return False
    
    def check_server_status(self):
        """检查服务器状态"""
        print("\n🔍 检查服务器状态...")
        
        # 检查端口
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 5000))
            sock.close()
            
            if result == 0:
                print("✅ 端口5000正在监听")
            else:
                print("❌ 端口5000未被占用")
                return False
        except Exception as e:
            print(f"❌ 端口检查失败: {e}")
            return False
        
        # 检查进程
        try:
            import psutil
            server_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'python3' and any('agent_server' in cmd for cmd in proc.info['cmdline']):
                        server_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if server_processes:
                print(f"✅ 找到 {len(server_processes)} 个服务器进程:")
                for proc in server_processes:
                    print(f"  PID {proc['pid']}: {proc['cmdline']}")
                return True
            else:
                print("❌ 未找到服务器进程")
                return False
        except Exception as e:
            print(f"❌ 进程检查失败: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        if self.server_process:
            print("\n🛑 停止服务器...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                print("✅ 服务器已停止")
            except subprocess.TimeoutExpired:
                print("⚠️  服务器强制终止")
                self.server_process.kill()

async def main():
    """主函数"""
    print("🚀 Injective Agent API 快速启动工具")
    print("=" * 50)
    
    quick_start = QuickStart()
    
    try:
        # 检查命令行参数
        if len(sys.argv) > 1:
            if sys.argv[1] == "--start":
                # 启动服务器
                if quick_start.start_server(background=True):
                    print("✅ 服务器启动成功")
                    # 不要在这里调用cleanup，让服务器继续运行
                    return
                else:
                    print("❌ 服务器启动失败")
            elif sys.argv[1] == "--stop":
                # 停止服务器
                if quick_start.stop_server():
                    print("✅ 服务器停止成功")
                else:
                    print("❌ 服务器停止失败")
            elif sys.argv[1] == "--status":
                # 检查服务器状态
                if quick_start.check_server_status():
                    print("✅ 服务器运行正常")
                else:
                    print("❌ 服务器未运行")
            elif sys.argv[1] == "--check":
                # 检查环境和依赖
                if quick_start.check_dependencies() and quick_start.check_environment():
                    print("✅ 环境检查完成，所有依赖都已安装")
                else:
                    print("❌ 环境检查失败，请检查上述问题")
            else:
                print("❌ 无效参数")
                print("用法:")
                print("  python quick_start_service.py --start   # 启动服务器")
                print("  python quick_start_service.py --stop    # 停止服务器")
                print("  python quick_start_service.py --status  # 检查状态")
                print("  python quick_start_service.py --check   # 检查环境")
                print("  python quick_start_service.py           # 交互式菜单")
        else:
            # 交互式菜单
            await quick_start.interactive_menu()
    
    except KeyboardInterrupt:
        print("\n\n🛑 操作被中断")
        # 只有在交互式模式下才清理
        if len(sys.argv) == 1:
            quick_start.cleanup()
    except Exception as e:
        print(f"\n💥 发生错误: {e}")
        # 只有在交互式模式下才清理
        if len(sys.argv) == 1:
            quick_start.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
