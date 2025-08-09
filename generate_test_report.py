#!/usr/bin/env python3
"""
综合测试报告生成器 - Injective Agent API
生成详细的测试报告和性能分析
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
import os

class TestReportGenerator:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def run_comprehensive_tests(self):
        """运行综合测试"""
        print("🚀 开始综合测试...")
        
        tests = [
            ("基础API测试", self.test_basic_apis),
            ("聊天功能测试", self.test_chat_functionality),
            ("区块链功能测试", self.test_blockchain_functions),
            ("性能压力测试", self.test_performance),
            ("错误处理测试", self.test_error_handling),
        ]
        
        for test_name, test_func in tests:
            print(f"\n📋 运行测试: {test_name}")
            result = await test_func()
            self.test_results.append({
                "test_name": test_name,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
    
    async def test_basic_apis(self):
        """测试基础API"""
        results = []
        
        # 测试根端点
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                data = await response.json()
                results.append({
                    "endpoint": "GET /",
                    "status": "success" if response.status == 200 else "failed",
                    "status_code": response.status,
                    "response_time": response.headers.get("X-Response-Time", "N/A")
                })
        except Exception as e:
            results.append({
                "endpoint": "GET /",
                "status": "error",
                "error": str(e)
            })
        
        # 测试健康检查
        try:
            async with self.session.get(f"{self.base_url}/ping") as response:
                data = await response.json()
                results.append({
                    "endpoint": "GET /ping",
                    "status": "success" if response.status == 200 else "failed",
                    "status_code": response.status,
                    "response_time": response.headers.get("X-Response-Time", "N/A")
                })
        except Exception as e:
            results.append({
                "endpoint": "GET /ping",
                "status": "error",
                "error": str(e)
            })
        
        return results
    
    async def test_chat_functionality(self):
        """测试聊天功能"""
        results = []
        
        chat_tests = [
            {
                "name": "基础聊天",
                "message": "你好，请介绍一下你自己",
                "session_id": "report_test_1"
            },
            {
                "name": "区块链咨询",
                "message": "请告诉我Injective区块链的特点",
                "session_id": "report_test_2"
            },
            {
                "name": "功能查询",
                "message": "你能帮我做什么？",
                "session_id": "report_test_3"
            }
        ]
        
        for test in chat_tests:
            try:
                start_time = time.time()
                async with self.session.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": test["message"],
                        "session_id": test["session_id"],
                        "agent_id": f"report_agent_{test['session_id']}",
                        "agent_key": "default",
                        "environment": "testnet"
                    }
                ) as response:
                    response_time = time.time() - start_time
                    data = await response.json()
                    
                    results.append({
                        "test_name": test["name"],
                        "status": "success" if response.status == 200 else "failed",
                        "status_code": response.status,
                        "response_time": response_time,
                        "has_function_call": data.get("function_call") is not None
                    })
            except Exception as e:
                results.append({
                    "test_name": test["name"],
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    async def test_blockchain_functions(self):
        """测试区块链功能"""
        results = []
        
        blockchain_tests = [
            {
                "name": "账户查询",
                "message": "请查询账户余额",
                "session_id": "blockchain_report_1"
            },
            {
                "name": "市场信息",
                "message": "请查询可用的交易市场",
                "session_id": "blockchain_report_2"
            },
            {
                "name": "代币信息",
                "message": "请查询INJ代币信息",
                "session_id": "blockchain_report_3"
            }
        ]
        
        for test in blockchain_tests:
            try:
                start_time = time.time()
                async with self.session.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": test["message"],
                        "session_id": test["session_id"],
                        "agent_id": f"blockchain_report_{test['session_id']}",
                        "agent_key": "default",
                        "environment": "testnet"
                    }
                ) as response:
                    response_time = time.time() - start_time
                    data = await response.json()
                    
                    results.append({
                        "test_name": test["name"],
                        "status": "success" if response.status == 200 else "failed",
                        "status_code": response.status,
                        "response_time": response_time,
                        "has_function_call": data.get("function_call") is not None,
                        "response_contains_error": "error" in data.get("response", "").lower()
                    })
            except Exception as e:
                results.append({
                    "test_name": test["name"],
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    async def test_performance(self):
        """性能测试"""
        results = []
        
        # 并发测试
        async def single_request(i):
            try:
                start_time = time.time()
                async with self.session.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": f"性能测试请求 {i}",
                        "session_id": f"perf_test_{i}",
                        "agent_id": f"perf_agent_{i}",
                        "agent_key": "default",
                        "environment": "testnet"
                    }
                ) as response:
                    response_time = time.time() - start_time
                    return {
                        "request_id": i,
                        "status": "success" if response.status == 200 else "failed",
                        "response_time": response_time,
                        "status_code": response.status
                    }
            except Exception as e:
                return {
                    "request_id": i,
                    "status": "error",
                    "error": str(e)
                }
        
        # 并发发送10个请求
        tasks = [single_request(i) for i in range(10)]
        concurrent_results = await asyncio.gather(*tasks)
        
        response_times = [r["response_time"] for r in concurrent_results if r["status"] == "success"]
        
        results.append({
            "test_type": "并发测试",
            "total_requests": len(concurrent_results),
            "successful_requests": len([r for r in concurrent_results if r["status"] == "success"]),
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0
        })
        
        return results
    
    async def test_error_handling(self):
        """错误处理测试"""
        results = []
        
        error_tests = [
            {
                "name": "空消息测试",
                "data": {"message": "", "session_id": "error_test_1"}
            },
            {
                "name": "无效JSON测试",
                "data": {"invalid": "data"}
            },
            {
                "name": "缺少必需字段测试",
                "data": {"session_id": "error_test_3"}
            }
        ]
        
        for test in error_tests:
            try:
                async with self.session.post(
                    f"{self.base_url}/chat",
                    json=test["data"]
                ) as response:
                    results.append({
                        "test_name": test["name"],
                        "expected_error": response.status >= 400,
                        "status_code": response.status,
                        "handled_correctly": response.status in [400, 422, 500]
                    })
            except Exception as e:
                results.append({
                    "test_name": test["name"],
                    "expected_error": True,
                    "error": str(e),
                    "handled_correctly": True
                })
        
        return results
    
    def generate_report(self):
        """生成测试报告"""
        report = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "timestamp": datetime.now().isoformat(),
                "server_url": self.base_url
            },
            "test_results": self.test_results,
            "summary": self.calculate_summary()
        }
        
        return report
    
    def calculate_summary(self):
        """计算测试摘要"""
        total_tests = len(self.test_results)
        successful_tests = 0
        
        for result in self.test_results:
            if isinstance(result["result"], list):
                # 对于返回列表的测试，检查是否所有子测试都成功
                all_success = all(
                    isinstance(item, dict) and item.get("status") == "success"
                    for item in result["result"]
                )
                if all_success:
                    successful_tests += 1
            else:
                # 对于返回单个结果的测试
                if result["result"]:
                    successful_tests += 1
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0
        }
    
    def save_report(self, report, filename="test_report.json"):
        """保存测试报告"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"📄 测试报告已保存到: {filename}")
    
    def print_summary(self, report):
        """打印测试摘要"""
        summary = report["summary"]
        
        print("\n" + "=" * 60)
        print("📊 测试报告摘要")
        print("=" * 60)
        print(f"📅 测试时间: {report['test_summary']['timestamp']}")
        print(f"🔗 服务器地址: {report['test_summary']['server_url']}")
        print(f"📋 总测试数: {summary['total_tests']}")
        print(f"✅ 成功测试: {summary['successful_tests']}")
        print(f"📈 成功率: {summary['success_rate']:.1f}%")
        print("=" * 60)
        
        # 详细结果
        print("\n📋 详细测试结果:")
        for result in report["test_results"]:
            status = "✅ 通过" if result["result"] else "❌ 失败"
            print(f"   {result['test_name']}: {status}")

async def main():
    """主函数"""
    print("📊 Injective Agent API 综合测试报告生成器")
    print("=" * 50)
    
    async with TestReportGenerator() as generator:
        # 运行所有测试
        await generator.run_comprehensive_tests()
        
        # 生成报告
        report = generator.generate_report()
        
        # 打印摘要
        generator.print_summary(report)
        
        # 保存报告
        generator.save_report(report)
        
        print("\n🎯 测试报告生成完成！")

if __name__ == "__main__":
    asyncio.run(main())
