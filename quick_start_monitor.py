#!/usr/bin/env python3
"""
统一监控工具 - Injective Agent API
📊 整合所有监控功能的统一界面
功能：实时监控、系统状态、性能分析、日志查看、健康检查

整合来源：monitor_server.py + server_status.py
新文件名：quick_start_monitor.py
"""

import asyncio
import aiohttp
import json
import time
import psutil
import os
import sys
import signal
from datetime import datetime
from collections import deque
from typing import Dict, List, Optional
import subprocess


class UnifiedMonitor:
    """统一监控系统 - 整合所有监控功能"""
    
    def __init__(self, base_url="http://localhost:5000", interval=5):
        self.base_url = base_url
        self.interval = interval
        self.session = None
        
        # 性能监控数据
        self.response_times = deque(maxlen=100)
        self.error_count = 0
        self.success_count = 0
        self.status_history = deque(maxlen=50)
        
        # 系统监控数据
        self.cpu_history = deque(maxlen=60)  # 1分钟历史
        self.memory_history = deque(maxlen=60)
        
        # 监控状态
        self.running = False
        self.start_time = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_system_info(self) -> Dict:
        """获取详细系统信息"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 网络信息
            net_io = psutil.net_io_counters()
            
            # 进程信息
            process_count = len(psutil.pids())
            
            system_info = {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
                },
                "memory": {
                    "percent": memory.percent,
                    "used_gb": memory.used / (1024**3),
                    "total_gb": memory.total / (1024**3),
                    "available_gb": memory.available / (1024**3)
                },
                "disk": {
                    "percent": disk.percent,
                    "used_gb": disk.used / (1024**3),
                    "total_gb": disk.total / (1024**3),
                    "free_gb": disk.free / (1024**3)
                },
                "network": {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv
                },
                "process_count": process_count
            }
            
            # 更新历史数据
            self.cpu_history.append(cpu_percent)
            self.memory_history.append(memory.percent)
            
            return system_info
        except Exception as e:
            return {"error": str(e)}
    
    def get_injective_processes(self) -> List[Dict]:
        """获取Injective相关进程信息"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'cmdline']):
                try:
                    if any(keyword in ' '.join(proc.info['cmdline'] or []).lower() 
                          for keyword in ['agent_server', 'injective', 'quick_start']):
                        processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cpu_percent": proc.info['cpu_percent'],
                            "memory_percent": proc.info['memory_percent'],
                            "cmdline": ' '.join(proc.info['cmdline'] or [])
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"获取进程信息时出错: {e}")
        
        return processes
    
    async def test_server_health(self) -> Dict:
        """测试服务器健康状态"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "endpoints": {},
            "overall_status": "unknown",
            "response_time_avg": 0
        }
        
        endpoints = [
            ("/", "GET", "根端点"),
            ("/ping", "GET", "健康检查"),
            ("/history", "GET", "历史记录")
        ]
        
        total_response_time = 0
        successful_tests = 0
        
        for endpoint, method, description in endpoints:
            try:
                start_time = time.time()
                
                if method == "GET":
                    async with self.session.get(f"{self.base_url}{endpoint}") as response:
                        response_time = time.time() - start_time
                        
                        health_status["endpoints"][endpoint] = {
                            "status": "healthy" if response.status == 200 else "unhealthy",
                            "response_code": response.status,
                            "response_time": response_time,
                            "description": description
                        }
                        
                        if response.status == 200:
                            successful_tests += 1
                            total_response_time += response_time
                            self.success_count += 1
                        else:
                            self.error_count += 1
                        
                        self.response_times.append(response_time)
                        
            except Exception as e:
                health_status["endpoints"][endpoint] = {
                    "status": "error",
                    "error": str(e),
                    "description": description
                }
                self.error_count += 1
        
        # 计算整体状态
        if successful_tests == len(endpoints):
            health_status["overall_status"] = "healthy"
        elif successful_tests > 0:
            health_status["overall_status"] = "degraded"
        else:
            health_status["overall_status"] = "unhealthy"
        
        if successful_tests > 0:
            health_status["response_time_avg"] = total_response_time / successful_tests
        
        return health_status
    
    def get_performance_stats(self) -> Dict:
        """获取性能统计信息"""
        total_requests = self.success_count + self.error_count
        success_rate = (self.success_count / total_requests * 100) if total_requests > 0 else 0
        
        response_times_list = list(self.response_times)
        avg_response_time = sum(response_times_list) / len(response_times_list) if response_times_list else 0
        max_response_time = max(response_times_list) if response_times_list else 0
        min_response_time = min(response_times_list) if response_times_list else 0
        
        return {
            "total_requests": total_requests,
            "successful_requests": self.success_count,
            "failed_requests": self.error_count,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time,
            "uptime": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        }
    
    def display_dashboard(self, system_info: Dict, health_status: Dict, performance_stats: Dict):
        """显示监控面板"""
        # 清屏
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("=" * 80)
        print("🔍 Injective Agent API 统一监控面板")
        print(f"⏰ 监控时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 服务器地址: {self.base_url}")
        print("=" * 80)
        
        # 系统信息
        if "error" not in system_info:
            print("\n📊 系统状态:")
            print(f"  💻 CPU使用率: {system_info['cpu']['percent']:.1f}%")
            print(f"  💾 内存使用率: {system_info['memory']['percent']:.1f}% ({system_info['memory']['used_gb']:.1f}GB / {system_info['memory']['total_gb']:.1f}GB)")
            print(f"  💿 磁盘使用率: {system_info['disk']['percent']:.1f}% ({system_info['disk']['used_gb']:.1f}GB / {system_info['disk']['total_gb']:.1f}GB)")
            print(f"  🔄 进程数量: {system_info['process_count']}")
        
        # 服务器健康状态
        print(f"\n🏥 服务器健康状态: {health_status['overall_status'].upper()}")
        for endpoint, status in health_status['endpoints'].items():
            status_icon = "✅" if status['status'] == 'healthy' else "❌" if status['status'] == 'unhealthy' else "⚠️"
            if 'response_time' in status:
                print(f"  {status_icon} {endpoint}: {status['response_code']} ({status['response_time']:.3f}s)")
            else:
                print(f"  {status_icon} {endpoint}: {status.get('error', 'Unknown error')}")
        
        # 性能统计
        print(f"\n📈 性能统计:")
        print(f"  📊 请求总数: {performance_stats['total_requests']}")
        print(f"  ✅ 成功率: {performance_stats['success_rate']:.1f}%")
        print(f"  ⚡ 平均响应时间: {performance_stats['avg_response_time']:.3f}s")
        print(f"  📌 最快/最慢: {performance_stats['min_response_time']:.3f}s / {performance_stats['max_response_time']:.3f}s")
        print(f"  ⏱️ 运行时间: {performance_stats['uptime']:.0f}s")
        
        # Injective进程
        processes = self.get_injective_processes()
        if processes:
            print(f"\n🔧 Injective相关进程:")
            for proc in processes:
                print(f"  PID {proc['pid']}: {proc['name']} (CPU: {proc['cpu_percent']:.1f}%, MEM: {proc['memory_percent']:.1f}%)")
        
        print(f"\n⌨️ 按 Ctrl+C 停止监控")
        print("=" * 80)
    
    async def start_monitoring(self):
        """开始监控"""
        print("🚀 启动统一监控系统...")
        self.running = True
        self.start_time = datetime.now()
        
        # 设置信号处理
        def signal_handler(signum, frame):
            print("\n\n🛑 监控已停止")
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            while self.running:
                # 获取系统信息
                system_info = self.get_system_info()
                
                # 测试服务器健康状态
                health_status = await self.test_server_health()
                
                # 获取性能统计
                performance_stats = self.get_performance_stats()
                
                # 显示面板
                self.display_dashboard(system_info, health_status, performance_stats)
                
                # 等待间隔
                await asyncio.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 监控已停止")
        except Exception as e:
            print(f"\n💥 监控出错: {e}")
        finally:
            self.running = False
    
    async def generate_report(self) -> Dict:
        """生成监控报告"""
        print("📋 生成监控报告...")
        
        system_info = self.get_system_info()
        health_status = await self.test_server_health()
        performance_stats = self.get_performance_stats()
        processes = self.get_injective_processes()
        
        report = {
            "report_time": datetime.now().isoformat(),
            "monitor_config": {
                "base_url": self.base_url,
                "interval": self.interval
            },
            "system_info": system_info,
            "server_health": health_status,
            "performance_stats": performance_stats,
            "injective_processes": processes
        }
        
        # 保存报告
        report_file = f"monitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 报告已保存到: {report_file}")
        return report
    
    def show_menu(self):
        """显示菜单"""
        print("\n" + "=" * 50)
        print("📊 Injective Agent API 统一监控工具")
        print("=" * 50)
        print("1. 启动实时监控")
        print("2. 生成监控报告")
        print("3. 查看系统信息")
        print("4. 测试服务器健康")
        print("5. 查看进程信息")
        print("6. 退出")
        print("=" * 50)


async def run_interactive_monitor():
    """运行交互式监控"""
    base_url = "http://localhost:5000"
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1].startswith("http"):
            base_url = sys.argv[1]
    
    async with UnifiedMonitor(base_url) as monitor:
        while True:
            monitor.show_menu()
            
            try:
                choice = input("\n请选择操作 (1-6): ").strip()
                
                if choice == "1":
                    # 启动实时监控
                    await monitor.start_monitoring()
                
                elif choice == "2":
                    # 生成监控报告
                    await monitor.generate_report()
                    input("\n按回车键继续...")
                
                elif choice == "3":
                    # 查看系统信息
                    system_info = monitor.get_system_info()
                    print("\n📊 当前系统信息:")
                    print(json.dumps(system_info, indent=2, ensure_ascii=False))
                    input("\n按回车键继续...")
                
                elif choice == "4":
                    # 测试服务器健康
                    print("\n🏥 测试服务器健康状态...")
                    health_status = await monitor.test_server_health()
                    print(json.dumps(health_status, indent=2, ensure_ascii=False))
                    input("\n按回车键继续...")
                
                elif choice == "5":
                    # 查看进程信息
                    processes = monitor.get_injective_processes()
                    print(f"\n🔧 Injective相关进程 ({len(processes)}个):")
                    for proc in processes:
                        print(f"  PID {proc['pid']}: {proc['name']}")
                        print(f"    CPU: {proc['cpu_percent']:.1f}%, 内存: {proc['memory_percent']:.1f}%")
                        print(f"    命令: {proc['cmdline'][:80]}...")
                    input("\n按回车键继续...")
                
                elif choice == "6":
                    print("👋 再见！")
                    break
                
                else:
                    print("❌ 无效选择，请重新输入")
                    input("\n按回车键继续...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 操作失败: {e}")
                input("\n按回车键继续...")


async def main():
    """主函数"""
    print("📊 Injective Agent API 统一监控工具")
    print("=" * 50)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--auto":
            # 自动监控模式
            async with UnifiedMonitor() as monitor:
                await monitor.start_monitoring()
        elif sys.argv[1] == "--report":
            # 生成报告模式
            async with UnifiedMonitor() as monitor:
                await monitor.generate_report()
        elif sys.argv[1] == "--help":
            print("用法:")
            print("  python quick_start_monitor.py              # 交互式菜单")
            print("  python quick_start_monitor.py --auto       # 自动监控")
            print("  python quick_start_monitor.py --report     # 生成报告")
            print("  python quick_start_monitor.py <URL>        # 指定服务器地址")
        else:
            # 指定URL
            async with UnifiedMonitor(sys.argv[1]) as monitor:
                await run_interactive_monitor()
    else:
        # 交互式菜单
        await run_interactive_monitor()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
    except Exception as e:
        print(f"💥 发生错误: {e}")
