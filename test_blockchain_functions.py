#!/usr/bin/env python3
"""
区块链功能测试脚本 - Injective Agent API
测试区块链相关的功能调用
"""

import asyncio
import aiohttp
import json
from datetime import datetime

class BlockchainFunctionTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_blockchain_queries(self):
        """测试区块链查询功能"""
        print("🔍 测试区块链查询功能...")
        
        queries = [
            {
                "name": "查询账户余额",
                "message": "请帮我查询账户余额",
                "session_id": "blockchain_test_1"
            },
            {
                "name": "查询市场信息",
                "message": "请告诉我当前可用的交易市场",
                "session_id": "blockchain_test_2"
            },
            {
                "name": "查询代币信息",
                "message": "请查询INJ代币的详细信息",
                "session_id": "blockchain_test_3"
            },
            {
                "name": "查询网络状态",
                "message": "请告诉我Injective网络的状态信息",
                "session_id": "blockchain_test_4"
            }
        ]
        
        results = []
        for i, query in enumerate(queries, 1):
            print(f"\n   测试 {i}: {query['name']}")
            try:
                async with self.session.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": query["message"],
                        "session_id": query["session_id"],
                        "agent_id": f"blockchain_agent_{i}",
                        "agent_key": "default",
                        "environment": "testnet"
                    }
                ) as response:
                    data = await response.json()
                    print(f"   ✅ 测试 {i} 成功")
                    print(f"      状态码: {response.status}")
                    print(f"      响应: {json.dumps(data, indent=4, ensure_ascii=False)}")
                    results.append(True)
            except Exception as e:
                print(f"   ❌ 测试 {i} 失败: {e}")
                results.append(False)
        
        return all(results)
    
    async def test_trading_functions(self):
        """测试交易功能"""
        print("\n🔍 测试交易功能...")
        
        trading_tests = [
            {
                "name": "查询订单簿",
                "message": "请查询INJ/USDT的订单簿信息",
                "session_id": "trading_test_1"
            },
            {
                "name": "查询历史价格",
                "message": "请查询INJ代币的历史价格数据",
                "session_id": "trading_test_2"
            },
            {
                "name": "查询交易对",
                "message": "请列出所有可用的交易对",
                "session_id": "trading_test_3"
            }
        ]
        
        results = []
        for i, test in enumerate(trading_tests, 1):
            print(f"\n   测试 {i}: {test['name']}")
            try:
                async with self.session.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": test["message"],
                        "session_id": test["session_id"],
                        "agent_id": f"trading_agent_{i}",
                        "agent_key": "default",
                        "environment": "testnet"
                    }
                ) as response:
                    data = await response.json()
                    print(f"   ✅ 测试 {i} 成功")
                    print(f"      状态码: {response.status}")
                    print(f"      响应: {json.dumps(data, indent=4, ensure_ascii=False)}")
                    results.append(True)
            except Exception as e:
                print(f"   ❌ 测试 {i} 失败: {e}")
                results.append(False)
        
        return all(results)
    
    async def test_staking_functions(self):
        """测试质押功能"""
        print("\n🔍 测试质押功能...")
        
        staking_tests = [
            {
                "name": "查询验证者",
                "message": "请列出当前的验证者信息",
                "session_id": "staking_test_1"
            },
            {
                "name": "查询质押奖励",
                "message": "请告诉我质押INJ的奖励机制",
                "session_id": "staking_test_2"
            },
            {
                "name": "查询质押状态",
                "message": "请查询当前的质押状态",
                "session_id": "staking_test_3"
            }
        ]
        
        results = []
        for i, test in enumerate(staking_tests, 1):
            print(f"\n   测试 {i}: {test['name']}")
            try:
                async with self.session.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": test["message"],
                        "session_id": test["session_id"],
                        "agent_id": f"staking_agent_{i}",
                        "agent_key": "default",
                        "environment": "testnet"
                    }
                ) as response:
                    data = await response.json()
                    print(f"   ✅ 测试 {i} 成功")
                    print(f"      状态码: {response.status}")
                    print(f"      响应: {json.dumps(data, indent=4, ensure_ascii=False)}")
                    results.append(True)
            except Exception as e:
                print(f"   ❌ 测试 {i} 失败: {e}")
                results.append(False)
        
        return all(results)
    
    async def test_advanced_functions(self):
        """测试高级功能"""
        print("\n🔍 测试高级功能...")
        
        advanced_tests = [
            {
                "name": "智能合约交互",
                "message": "请解释如何在Injective上部署智能合约",
                "session_id": "advanced_test_1"
            },
            {
                "name": "跨链功能",
                "message": "请说明Injective的跨链功能",
                "session_id": "advanced_test_2"
            },
            {
                "name": "治理功能",
                "message": "请解释Injective的治理机制",
                "session_id": "advanced_test_3"
            }
        ]
        
        results = []
        for i, test in enumerate(advanced_tests, 1):
            print(f"\n   测试 {i}: {test['name']}")
            try:
                async with self.session.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": test["message"],
                        "session_id": test["session_id"],
                        "agent_id": f"advanced_agent_{i}",
                        "agent_key": "default",
                        "environment": "testnet"
                    }
                ) as response:
                    data = await response.json()
                    print(f"   ✅ 测试 {i} 成功")
                    print(f"      状态码: {response.status}")
                    print(f"      响应: {json.dumps(data, indent=4, ensure_ascii=False)}")
                    results.append(True)
            except Exception as e:
                print(f"   ❌ 测试 {i} 失败: {e}")
                results.append(False)
        
        return all(results)
    
    async def run_blockchain_tests(self):
        """运行所有区块链功能测试"""
        print("🚀 开始区块链功能测试")
        print("=" * 50)
        
        tests = [
            ("区块链查询", self.test_blockchain_queries),
            ("交易功能", self.test_trading_functions),
            ("质押功能", self.test_staking_functions),
            ("高级功能", self.test_advanced_functions),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n📋 运行测试: {test_name}")
            result = await test_func()
            results.append((test_name, result))
        
        # 输出测试结果摘要
        print("\n" + "=" * 50)
        print("📊 区块链功能测试结果:")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\n总计: {passed}/{total} 个测试通过")
        
        if passed == total:
            print("🎉 所有区块链功能测试通过！")
        else:
            print("⚠️  部分区块链功能测试失败")
        
        return passed == total

async def main():
    """主函数"""
    print("🔗 Injective 区块链功能测试工具")
    print("=" * 50)
    
    async with BlockchainFunctionTester() as tester:
        success = await tester.run_blockchain_tests()
        
        if success:
            print("\n🎯 区块链功能测试完成！所有功能正常")
        else:
            print("\n⚠️  区块链功能测试完成，发现问题")

if __name__ == "__main__":
    asyncio.run(main())
