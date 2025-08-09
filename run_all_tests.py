#!/usr/bin/env python3
"""
一键运行所有测试脚本 - Injective Agent API
自动运行所有测试并生成综合报告
"""

import asyncio
import subprocess
import sys
import time
import json
from datetime import datetime

class TestRunner:
    def __init__(self):
        self.results = {}
        self.start_time = None
        
    def run_command(self, command, description):
        """运行命令并返回结果"""
        print(f"\n🔍 {description}")
        print(f"   执行命令: {command}")
        
        try:
            start_time = time.time()
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            end_time = time.time()
            
            success = result.returncode == 0
            duration = end_time - start_time
            
            if success:
                print(f"   ✅ 成功 ({duration:.2f}s)")
            else:
                print(f"   ❌ 失败 ({duration:.2f}s)")
                print(f"   错误: {result.stderr}")
            
            return {
                "success": success,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            print(f"   ⏰ 超时 (300s)")
            return {
                "success": False,
                "duration": 300,
                "stdout": "",
                "stderr": "Command timed out",
                "returncode": -1
            }
        except Exception as e:
            print(f"   💥 异常: {e}")
            return {
                "success": False,
                "duration": 0,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def check_server_status(self):
        """检查服务器状态"""
        print("\n🔍 检查服务器状态...")
        
        try:
            import aiohttp
            import asyncio
            
            async def check():
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get("http://localhost:5000/ping", timeout=5) as response:
                            if response.status == 200:
                                return True
                            else:
                                return False
                except:
                    return False
            
            return asyncio.run(check())
        except:
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 Injective Agent API 一键测试套件")
        print("=" * 60)
        
        self.start_time = datetime.now()
        
        # 测试列表
        tests = [
            {
                "name": "基础API测试",
                "command": f"{sys.executable} test_agent_api.py",
                "description": "运行基础API功能测试"
            },
            {
                "name": "区块链功能测试",
                "command": f"{sys.executable} test_blockchain_functions.py",
                "description": "运行区块链功能测试"
            },
            {
                "name": "综合测试报告",
                "command": f"{sys.executable} generate_test_report.py",
                "description": "生成综合测试报告"
            }
        ]
        
        # 检查服务器状态
        if not self.check_server_status():
            print("⚠️  服务器未运行，请先启动服务器:")
            print("   python agent_server.py --port 5000")
            return False
        
        print("✅ 服务器运行正常，开始测试...")
        
        # 运行所有测试
        for test in tests:
            result = self.run_command(test["command"], test["description"])
            self.results[test["name"]] = result
        
        return True
    
    def generate_summary_report(self):
        """生成摘要报告"""
        if not self.results:
            return
        
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        # 计算统计信息
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results.values() if r["success"])
        total_duration_tests = sum(r["duration"] for r in self.results.values())
        
        # 生成报告
        report = {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration": total_duration,
                "test_duration": total_duration_tests,
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat()
            },
            "test_results": self.results
        }
        
        # 保存报告
        with open("all_tests_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 打印摘要
        print("\n" + "=" * 60)
        print("📊 测试摘要报告")
        print("=" * 60)
        print(f"📅 开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📅 结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  总耗时: {total_duration:.2f}秒")
        print(f"📋 总测试数: {total_tests}")
        print(f"✅ 成功测试: {successful_tests}")
        print(f"❌ 失败测试: {total_tests - successful_tests}")
        print(f"📈 成功率: {report['summary']['success_rate']:.1f}%")
        print("=" * 60)
        
        # 详细结果
        print("\n📋 详细结果:")
        for test_name, result in self.results.items():
            status = "✅ 通过" if result["success"] else "❌ 失败"
            print(f"   {test_name}: {status} ({result['duration']:.2f}s)")
        
        print(f"\n📄 详细报告已保存到: all_tests_report.json")
        
        # 最终状态
        if successful_tests == total_tests:
            print("\n🎉 所有测试通过！")
            return True
        else:
            print(f"\n⚠️  {total_tests - successful_tests} 个测试失败")
            return False

def main():
    """主函数"""
    runner = TestRunner()
    
    try:
        success = runner.run_all_tests()
        if success:
            runner.generate_summary_report()
        else:
            print("\n❌ 测试执行失败")
    except KeyboardInterrupt:
        print("\n\n🛑 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试执行异常: {e}")

if __name__ == "__main__":
    main()
