#!/usr/bin/env python3
"""
无私钥测试脚本 - Injective Agent API
测试基础功能，不需要区块链私钥
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

class NoPrivateKeyTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_basic_functionality(self):
        """测试基础功能"""
        print("🔍 测试基础功能...")
        
        tests = [
            {
                "name": "基础聊天",
                "message": "你好，请介绍一下你自己",
                "session_id": "basic_test_1"
            },
            {
                "name": "功能查询",
                "message": "你能帮我做什么？",
                "session_id": "basic_test_2"
            },
            {
                "name": "Injective介绍",
                "message": "请介绍一下Injective区块链",
                "session_id": "basic_test_3"
            },
            {
                "name": "API信息",
                "message": "请告诉我这个API的功能",
                "session_id": "basic_test_4"
            }
        ]
        
        results = []
        for i, test in enumerate(tests, 1):
            print(f"\n   测试 {i}: {test['name']}")
            try:
                start_time = time.time()
                async with self.session.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": test["message"],
                        "session_id": test["session_id"],
                        "agent_id": f"basic_agent_{i}",
                        "agent_key": "default",  # 使用默认密钥
                        "environment": "testnet"
                    }
                ) as response:
                    response_time = time.time() - start_time
                    data = await response.json()
                    
                    if response.status == 200:
                        print(f"   ✅ 成功 ({response_time:.2f}s)")
                        # 检查响应是否包含错误信息
                        response_text = data.get("response", "")
                        if "error" in response_text.lower() or "accessdeny" in response_text.lower():
                            print(f"   ⚠️  响应包含错误信息")
                        else:
                            print(f"   📝 响应正常")
                        results.append(True)
                    else:
                        print(f"   ❌ 失败: HTTP {response.status}")
                        results.append(False)
            except Exception as e:
                print(f"   ❌ 异常: {e}")
                results.append(False)
        
        return results
    
    async def test_api_endpoints(self):
        """测试API端点"""
        print("\n🔍 测试API端点...")
        
        endpoints = [
            ("GET", "/", "根端点"),
            ("GET", "/ping", "健康检查"),
            ("GET", "/history?session_id=test", "历史记录"),
            ("POST", "/clear?session_id=test", "清除历史")
        ]
        
        results = []
        for method, endpoint, name in endpoints:
            print(f"   测试: {name} ({method} {endpoint})")
            try:
                if method == "GET":
                    async with self.session.get(f"{self.base_url}{endpoint}") as response:
                        if response.status == 200:
                            print(f"   ✅ 成功")
                            results.append(True)
                        else:
                            print(f"   ❌ 失败: HTTP {response.status}")
                            results.append(False)
                elif method == "POST":
                    async with self.session.post(f"{self.base_url}{endpoint}") as response:
                        if response.status == 200:
                            print(f"   ✅ 成功")
                            results.append(True)
                        else:
                            print(f"   ❌ 失败: HTTP {response.status}")
                            results.append(False)
            except Exception as e:
                print(f"   ❌ 异常: {e}")
                results.append(False)
        
        return results
    
    async def test_error_handling(self):
        """测试错误处理"""
        print("\n🔍 测试错误处理...")
        
        error_tests = [
            {
                "name": "空消息",
                "data": {"message": "", "session_id": "error_test_1"}
            },
            {
                "name": "无效JSON",
                "data": {"invalid": "data"}
            },
            {
                "name": "缺少必需字段",
                "data": {"session_id": "error_test_3"}
            }
        ]
        
        results = []
        for test in error_tests:
            print(f"   测试: {test['name']}")
            try:
                async with self.session.post(
                    f"{self.base_url}/chat",
                    json=test["data"]
                ) as response:
                    # 对于错误测试，我们期望得到错误响应
                    if response.status >= 400:
                        print(f"   ✅ 正确处理错误 (HTTP {response.status})")
                        results.append(True)
                    else:
                        print(f"   ⚠️  未正确处理错误 (HTTP {response.status})")
                        results.append(False)
            except Exception as e:
                print(f"   ❌ 异常: {e}")
                results.append(False)
        
        return results
    
    async def test_performance(self):
        """测试性能"""
        print("\n🔍 测试性能...")
        
        # 并发测试
        async def single_request(i):
            try:
                start_time = time.time()
                async with self.session.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": f"性能测试 {i}",
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
        
        # 并发发送5个请求
        print("   发送5个并发请求...")
        tasks = [single_request(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        successful_requests = [r for r in results if r["status"] == "success"]
        response_times = [r["response_time"] for r in successful_requests]
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            print(f"   ✅ 成功请求: {len(successful_requests)}/5")
            print(f"   ⏱️  平均响应时间: {avg_time:.2f}s")
            print(f"   ⏱️  最快响应时间: {min_time:.2f}s")
            print(f"   ⏱️  最慢响应时间: {max_time:.2f}s")
            
            return len(successful_requests) >= 3  # 至少3个成功
        else:
            print(f"   ❌ 所有请求都失败")
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 无私钥测试套件")
        print("=" * 50)
        
        tests = [
            ("基础功能测试", self.test_basic_functionality),
            ("API端点测试", self.test_api_endpoints),
            ("错误处理测试", self.test_error_handling),
            ("性能测试", self.test_performance)
        ]
        
        all_results = []
        for test_name, test_func in tests:
            print(f"\n📋 运行测试: {test_name}")
            result = await test_func()
            
            if isinstance(result, list):
                success_count = sum(result)
                total_count = len(result)
                success_rate = (success_count / total_count * 100) if total_count > 0 else 0
                print(f"   结果: {success_count}/{total_count} 通过 ({success_rate:.1f}%)")
                all_results.append(success_count >= total_count * 0.8)  # 80%成功率
            else:
                print(f"   结果: {'✅ 通过' if result else '❌ 失败'}")
                all_results.append(result)
        
        # 生成报告
        self.generate_report(all_results, tests)
        
        return all_results
    
    def generate_report(self, results, tests):
        """生成测试报告"""
        print("\n" + "=" * 50)
        print("📊 测试报告")
        print("=" * 50)
        
        total_tests = len(tests)
        successful_tests = sum(results)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📋 总测试数: {total_tests}")
        print(f"✅ 成功测试: {successful_tests}")
        print(f"❌ 失败测试: {total_tests - successful_tests}")
        print(f"📈 成功率: {success_rate:.1f}%")
        
        print("\n📋 详细结果:")
        for i, (test_name, _) in enumerate(tests):
            status = "✅ 通过" if results[i] else "❌ 失败"
            print(f"   {test_name}: {status}")
        
        if success_rate >= 80:
            print("\n🎉 测试总体通过！")
        else:
            print("\n⚠️  部分测试失败，请检查服务器状态")
        
        print("=" * 50)

async def main():
    """主函数"""
    print("🔧 Injective Agent API 无私钥测试工具")
    print("=" * 50)
    
    async with NoPrivateKeyTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
