#!/usr/bin/env python3
"""
统一启动工具 - Injective Agent API
🚀 集成服务器管理、客户端交互、监控管理的统一入口

功能模式：
- service: 服务器管理（环境检查、启动、测试）
- client: 客户端交互（代理管理、聊天交互）
- monitor: 监控管理（实时监控、报告生成）
- all: 一键启动全套服务

使用方法：
python3 quick_start.py [模式] [选项]
"""

import os
import sys
import time
import asyncio
import subprocess
import signal
from datetime import datetime
import argparse
import requests


class UnifiedQuickStart:
    """统一快速启动工具"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.processes = []  # 存储启动的进程
        
    def show_banner(self):
        """显示启动横幅"""
        print("=" * 80)
        print("🚀 Injective Agent API 统一启动工具")
        print("=" * 80)
        print("📋 可用模式:")
        print("  all      - 🎯 一键启动全套服务 ⭐ [推荐]")
        print("  service  - 🔧 服务器管理（环境检查、启动、测试）")
        print("  client   - 💬 客户端交互（代理管理、聊天交互）")
        print("  monitor  - 📊 监控管理（实时监控、报告生成）")
        print("=" * 80)
    
    def show_help(self):
        """显示帮助信息"""
        print("""
🚀 Injective Agent API 统一启动工具

使用方法:
  python3 quick_start.py [模式] [选项]

模式:
  service          服务器管理模式
  client           客户端交互模式  
  monitor          监控管理模式
  all              一键启动全套服务

服务器管理选项:
  --auto           自动部署和启动
  --test           运行测试套件
  --check          检查环境和依赖

客户端选项:
  --url URL        指定服务器地址 (默认: http://localhost:5000)
  --debug          启用调试模式

监控选项:
  --auto           自动监控模式
  --report         生成监控报告
  --url URL        指定监控目标服务器

全套启动选项:
  --auto           自动启动所有服务
  --detach         后台运行模式

示例:
  python3 quick_start.py                    # 交互式菜单（推荐，按回车即可一键启动）
  python3 quick_start.py all --auto         # 直接一键启动全套服务
  python3 quick_start.py service --auto     # 仅自动部署服务器
  python3 quick_start_client.py --debug     # 启动调试模式客户端
  python3 quick_start.py monitor --report   # 生成监控报告
        """)
    
    def run_service_mode(self, args):
        """运行服务器管理模式"""
        print("🔧 启动服务器管理模式...")
        
        service_script = os.path.join(self.base_dir, "quick_start_service.py")
        
        # 根据参数选择不同的服务器管理操作
        if hasattr(args, 'start') and args.start:
            # 启动服务器
            cmd = ["python3", service_script, "--start"]
        elif hasattr(args, 'stop') and args.stop:
            # 停止服务器
            cmd = ["python3", service_script, "--stop"]
        elif hasattr(args, 'status') and args.status:
            # 检查服务器状态
            cmd = ["python3", service_script, "--status"]
        elif hasattr(args, 'check') and args.check:
            # 检查环境和依赖
            cmd = ["python3", service_script, "--check"]
        elif hasattr(args, 'auto') and args.auto:
            # 自动模式，启动服务器
            cmd = ["python3", service_script, "--start"]
        else:
            # 默认启动服务器
            cmd = ["python3", service_script, "--start"]
        
        try:
            # 使用subprocess.Popen来启动服务器，这样可以在后台运行
            if "--start" in cmd:
                # 首先检查服务器是否已经运行
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', 5000))
                sock.close()
                
                if result == 0:
                    print("✅ 服务器已经在运行")
                    return True
                
                # 后台启动服务器
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.processes.append(process)
                
                # 等待一段时间让服务器启动
                time.sleep(5)
                
                # 检查端口是否被占用来判断服务器是否启动成功
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', 5000))
                sock.close()
                
                if result == 0:
                    print("✅ 服务器已在后台启动")
                    return True
                else:
                    print("❌ 服务器启动失败")
                    return False
            else:
                # 其他命令直接运行
                result = subprocess.run(cmd, check=True)
                print("✅ 服务器管理完成")
                return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"❌ 服务器管理失败: {e}")
            return False
        except FileNotFoundError:
            print(f"❌ 找不到服务器管理脚本: {service_script}")
            return False
    
    def run_client_mode(self, args):
        """运行客户端交互模式"""
        print("💬 启动客户端交互模式...")
        
        client_script = os.path.join(self.base_dir, "quick_start_client.py")
        cmd = ["python3", client_script]
        
        if hasattr(args, 'url') and args.url:
            cmd.extend(["--url", args.url])
        if hasattr(args, 'debug') and args.debug:
            cmd.append("--debug")
        
        try:
            # 客户端是交互式的，直接运行
            subprocess.run(cmd)
            return True
        except KeyboardInterrupt:
            print("\n💬 客户端已退出")
            return True
        except FileNotFoundError:
            print(f"❌ 找不到客户端脚本: {client_script}")
            return False
    
    def run_monitor_mode(self, args):
        """运行监控管理模式"""
        print("📊 启动监控管理模式...")
        
        monitor_script = os.path.join(self.base_dir, "quick_start_monitor.py")
        cmd = ["python3", monitor_script]
        
        if hasattr(args, 'auto') and args.auto:
            cmd.append("--auto")
        elif hasattr(args, 'report') and args.report:
            cmd.append("--report")
        elif hasattr(args, 'url') and args.url:
            cmd.append(args.url)
        
        try:
            subprocess.run(cmd)
            return True
        except KeyboardInterrupt:
            print("\n📊 监控已退出")
            return True
        except FileNotFoundError:
            print(f"❌ 找不到监控脚本: {monitor_script}")
            return False
    
    def run_all_mode(self, args):
        """运行一键启动全套服务模式"""
        print("🎯 启动一键全套服务模式...")
        
        detach = hasattr(args, 'detach') and args.detach
        
        try:
            # 1. 首先启动服务器
            print("\n📍 步骤 1/3: 启动服务器...")
            service_args = type('Args', (), {'auto': True})()
            if not self.run_service_mode(service_args):
                print("❌ 服务器启动失败，停止后续操作")
                return False
            
            print("✅ 服务器启动成功")
            time.sleep(3)  # 等待服务器完全启动
            
            # 2. 启动监控（后台模式）
            print("\n📍 步骤 2/3: 启动监控...")
            monitor_script = os.path.join(self.base_dir, "quick_start_monitor.py")
            
            if detach:
                # 后台运行监控
                monitor_process = subprocess.Popen([
                    "python3", monitor_script, "--auto"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.processes.append(monitor_process)
                print("✅ 监控已在后台启动")
            else:
                print("💡 监控将在新终端启动（需要手动运行）")
                print(f"   命令: python3 {monitor_script} --auto")
            
            # 3. 提供客户端启动选项
            print("\n📍 步骤 3/3: 客户端选项")
            print("🎉 全套服务启动完成！")
            print("\n📋 服务状态:")
            print("  🔧 服务器: http://localhost:5000")
            print("  📊 监控: 实时监控已启动" if detach else "监控: 需手动启动")
            print("  💬 客户端: 可随时连接")
            
            print("\n🚀 快速连接客户端:")
            print("  python3 quick_start_client.py")
            print("\n💡 提示: 直接运行 'python3 quick_start.py' 然后按回车即可一键启动全套服务")
            
            if not detach:
                # 交互模式，等待用户选择
                try:
                    while True:
                        choice = input("\n请选择操作 [c]客户端 [m]监控 [q]退出: ").strip().lower()
                        
                        if choice == 'c':
                            client_args = type('Args', (), {})()
                            self.run_client_mode(client_args)
                        elif choice == 'm':
                            monitor_args = type('Args', (), {'auto': True})()
                            self.run_monitor_mode(monitor_args)
                        elif choice == 'q':
                            break
                        else:
                            print("❌ 无效选择，请重新输入")
                except EOFError:
                    print("\n🤖 自动化模式，全套启动完成")
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n🛑 一键启动被中断")
            return False
        except Exception as e:
            print(f"❌ 一键启动失败: {e}")
            return False
    
    def interactive_menu(self):
        """交互式菜单"""
        while True:
            self.show_banner()
            print("\n请选择模式:")
            print("1. 🎯 一键启动全套 ⭐ [推荐]")
            print("2. 🔧 服务器管理")
            print("3. 💬 客户端交互")
            print("4. 📊 监控管理")
            print("5. ❓ 显示帮助")
            print("6. 🚪 退出")
            print("\n💡 提示: 输入 'q'、'quit'、'exit' 或 Ctrl+C 也可退出")
            
            try:
                choice = input("\n请选择 (1-6) [默认:1]: ").strip().lower()
                
                # 如果用户直接按回车，默认选择1（一键启动全套）
                if not choice:
                    choice = "1"
                
                # 支持多种退出方式
                if choice in ["6", "q", "quit", "exit", "退出"]:
                    print("👋 再见！")
                    break
                
                if choice == "1":
                    # 一键启动全套
                    try:
                        detach = input("是否后台运行监控? [y/N]: ").strip().lower() == 'y'
                    except EOFError:
                        # 自动化模式下默认不后台运行
                        detach = False
                        print("自动模式，使用默认设置")
                    args = type('Args', (), {'detach': detach, 'auto': True})()
                    self.run_all_mode(args)
                
                elif choice == "2":
                    # 服务器管理子菜单
                    print("\n🔧 服务器管理选项:")
                    print("1. 自动部署")
                    print("2. 运行测试")
                    print("3. 环境检查")
                    print("4. 停止服务器")
                    print("5. 查看服务器状态")
                    print("6. 关闭服务端 (HTTP /shutdown)")
                    sub_choice = input("请选择 (1-6): ").strip()
                    
                    if sub_choice == "1":
                        args = type('Args', (), {'auto': True})()
                        self.run_service_mode(args)
                    elif sub_choice == "2":
                        args = type('Args', (), {'test': True})()
                        self.run_service_mode(args)
                    elif sub_choice == "3":
                        args = type('Args', (), {'check': True})()
                        self.run_service_mode(args)
                    elif sub_choice == "4":
                        args = type('Args', (), {'stop': True})()
                        self.run_service_mode(args)
                    elif sub_choice == "5":
                        args = type('Args', (), {'status': True})()
                        self.run_service_mode(args)
                    elif sub_choice == "6":
                        # 调用 /shutdown 接口优雅关闭服务端
                        try:
                            url = "http://localhost:5000/shutdown"
                            token = input("如设置 SERVER_SHUTDOWN_TOKEN，请输入令牌（可留空）: ").strip()
                            payload = {"token": token} if token else {}
                            print("请求关闭服务端中...")
                            resp = requests.post(url, json=payload, timeout=5)
                            if resp.status_code == 200:
                                print("✅ 服务端已接收关闭请求")
                            elif resp.status_code == 403:
                                print("❌ 未授权，令牌无效或缺失")
                            else:
                                print(f"❌ 关闭失败: HTTP {resp.status_code} - {resp.text}")
                        except Exception as e:
                            print(f"❌ 关闭请求异常: {e}")
                
                elif choice == "3":
                    # 客户端交互
                    try:
                        debug = input("是否启用调试模式? [y/N]: ").strip().lower() == 'y'
                        url = input("服务器地址 [http://localhost:5000]: ").strip()
                        if not url:
                            url = "http://localhost:5000"
                    except EOFError:
                        # 自动化模式下使用默认设置
                        debug = False
                        url = "http://localhost:5000"
                        print("自动模式，使用默认设置")
                    
                    args = type('Args', (), {
                        'debug': debug,
                        'url': url
                    })()
                    self.run_client_mode(args)
                
                elif choice == "4":
                    # 监控管理子菜单
                    print("\n📊 监控管理选项:")
                    print("1. 实时监控")
                    print("2. 生成报告")
                    print("3. 指定服务器")
                    sub_choice = input("请选择 (1-3): ").strip()
                    
                    if sub_choice == "1":
                        args = type('Args', (), {'auto': True})()
                        self.run_monitor_mode(args)
                    elif sub_choice == "2":
                        args = type('Args', (), {'report': True})()
                        self.run_monitor_mode(args)
                    elif sub_choice == "3":
                        url = input("服务器地址: ").strip()
                        args = type('Args', (), {'url': url})()
                        self.run_monitor_mode(args)
                
                elif choice == "5":
                    self.show_help()
                    input("\n按回车键继续...")
                
                else:
                    print("❌ 无效选择，请重新输入")
                    time.sleep(1)
                    
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
                    print("\n🤖 自动化模式，继续运行...")
                    break
    
    def cleanup(self):
        """清理资源"""
        for process in self.processes:
            if process.poll() is None:  # 进程仍在运行
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()


def main():
    """主函数"""
    quick_start = UnifiedQuickStart()
    
    # 设置信号处理
    def signal_handler(signum, frame):
        print("\n\n🛑 程序被中断")
        quick_start.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        parser = argparse.ArgumentParser(
            description="Injective Agent API 统一启动工具",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # 添加位置参数（模式）
        parser.add_argument(
            'mode', 
            nargs='?', 
            choices=['service', 'client', 'monitor', 'all'],
            help='运行模式'
        )
        
        # 服务器管理选项
        parser.add_argument('--auto', action='store_true', help='自动模式')
        parser.add_argument('--test', action='store_true', help='测试模式')
        parser.add_argument('--check', action='store_true', help='检查模式')
        
        # 客户端选项
        parser.add_argument('--url', default='http://localhost:5000', help='服务器地址')
        parser.add_argument('--debug', action='store_true', help='调试模式')
        
        # 监控选项
        parser.add_argument('--report', action='store_true', help='生成报告')
        
        # 全套启动选项
        parser.add_argument('--detach', action='store_true', help='后台运行')
        
        args = parser.parse_args()
        
        if args.mode == 'service':
            quick_start.run_service_mode(args)
        elif args.mode == 'client':
            quick_start.run_client_mode(args)
        elif args.mode == 'monitor':
            quick_start.run_monitor_mode(args)
        elif args.mode == 'all':
            quick_start.run_all_mode(args)
        else:
            # 没有指定模式，显示交互菜单
            quick_start.interactive_menu()
            
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
    except Exception as e:
        print(f"💥 发生错误: {e}")
    finally:
        quick_start.cleanup()


if __name__ == "__main__":
    main()