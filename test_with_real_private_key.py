#!/usr/bin/env python3
"""
真实私钥测试脚本 - Injective Agent API
使用真实私钥测试完整的区块链功能
"""

import asyncio
import aiohttp
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv

class RealPrivateKeyTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = None
        self.private_key = None
        self.account_address = None
        
        # 加载环境变量
        load_dotenv()
        self.private_key = os.getenv("PRIVATE_KEY")
        self.account_address = os.getenv("ACCOUNT_ADDRESS")
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def check_private_key(self):
        """检查私钥配置"""
        print("🔑 检查私钥配置...")
        
        if not self.private_key:
            print("❌ 未找到PRIVATE_KEY环境变量")
            return False
        
        if not self.account_address:
            print("❌ 未找到ACCOUNT_ADDRESS环境变量")
            return False
        
        print(f"✅ 私钥已配置: {self.private_key[:8]}...")
        print(f"✅ 账户地址: {self.account_address}")
        return True
    
    async def test_account_balance(self):
        """测试账户余额查询"""
        print("\n🔍 测试账户余额查询...")
        
        tests = [
            {
                "name": "查询账户余额",
                "message": f"请查询账户 {self.account_address} 的余额",
                "session_id": "balance_test_1"
            },
            {
                "name": "查询INJ余额",
                "message": "请查询我的INJ代币余额",
                "session_id": "balance_test_2"
            },
            {
                "name": "查询所有代币",
                "message": "请查询我账户中的所有代币余额",
                "session_id": "balance_test_3"
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
                        "agent_id": f"balance_agent_{i}",
                        "agent_key": self.private_key,  # 使用真实私钥
                        "environment": "testnet"
                    }
                ) as response:
                    response_time = time.time() - start_time
                    data = await response.json()
                    
                    if response.status == 200:
                        print(f"   ✅ 成功 ({response_time:.2f}s)")
                        response_text = data.get("response", "")
                        
                        # 检查是否包含余额信息
                        if any(keyword in response_text.lower() for keyword in ["余额", "balance", "inj", "代币"]):
                            print(f"   📊 包含余额信息")
                            results.append(True)
                        else:
                            print(f"   ⚠️  未找到余额信息")
                            results.append(False)
                    else:
                        print(f"   ❌ 失败: HTTP {response.status}")
                        results.append(False)
            except Exception as e:
                print(f"   ❌ 异常: {e}")
                results.append(False)
        
        return results
    
    async def test_trading_functions(self):
        """测试交易功能"""
        print("\n🔍 测试交易功能...")
        
        tests = [
            {
                "name": "查询市场信息",
                "message": "请查询可用的交易市场",
                "session_id": "trading_test_1"
            },
            {
                "name": "查询订单簿",
                "message": "请查询INJ/USDT的订单簿",
                "session_id": "trading_test_2"
            },
            {
                "name": "查询历史价格",
                "message": "请查询INJ代币的历史价格",
                "session_id": "trading_test_3"
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
                        "agent_id": f"trading_agent_{i}",
                        "agent_key": self.private_key,
                        "environment": "testnet"
                    }
                ) as response:
                    response_time = time.time() - start_time
                    data = await response.json()
                    
                    if response.status == 200:
                        print(f"   ✅ 成功 ({response_time:.2f}s)")
                        response_text = data.get("response", "")
                        
                        # 检查是否包含交易相关信息
                        if any(keyword in response_text.lower() for keyword in ["市场", "market", "订单", "order", "价格", "price"]):
                            print(f"   📈 包含交易信息")
                            results.append(True)
                        else:
                            print(f"   ⚠️  未找到交易信息")
                            results.append(False)
                    else:
                        print(f"   ❌ 失败: HTTP {response.status}")
                        results.append(False)
            except Exception as e:
                print(f"   ❌ 异常: {e}")
                results.append(False)
        
        return results
    
    async def test_staking_functions(self):
        """测试质押功能"""
        print("\n🔍 测试质押功能...")
        
        tests = [
            {
                "name": "查询验证者",
                "message": "请查询当前的验证者列表",
                "session_id": "staking_test_1"
            },
            {
                "name": "查询质押状态",
                "message": f"请查询账户 {self.account_address} 的质押状态",
                "session_id": "staking_test_2"
            },
            {
                "name": "查询质押奖励",
                "message": "请查询质押INJ的奖励机制",
                "session_id": "staking_test_3"
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
                        "agent_id": f"staking_agent_{i}",
                        "agent_key": self.private_key,
                        "environment": "testnet"
                    }
                ) as response:
                    response_time = time.time() - start_time
                    data = await response.json()
                    
                    if response.status == 200:
                        print(f"   ✅ 成功 ({response_time:.2f}s)")
                        response_text = data.get("response", "")
                        
                        # 检查是否包含质押相关信息
                        if any(keyword in response_text.lower() for keyword in ["质押", "staking", "验证者", "validator", "奖励", "reward"]):
                            print(f"   🏦 包含质押信息")
                            results.append(True)
                        else:
                            print(f"   ⚠️  未找到质押信息")
                            results.append(False)
                    else:
                        print(f"   ❌ 失败: HTTP {response.status}")
                        results.append(False)
            except Exception as e:
                print(f"   ❌ 异常: {e}")
                results.append(False)
        
        return results
    
    async def test_governance_functions(self):
        """测试治理功能"""
        print("\n🔍 测试治理功能...")
        
        tests = [
            {
                "name": "查询提案",
                "message": "请查询当前的治理提案",
                "session_id": "governance_test_1"
            },
            {
                "name": "查询投票权",
                "message": f"请查询账户 {self.account_address} 的投票权",
                "session_id": "governance_test_2"
            },
            {
                "name": "查询治理参数",
                "message": "请查询Injective的治理参数",
                "session_id": "governance_test_3"
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
                        "agent_id": f"governance_agent_{i}",
                        "agent_key": self.private_key,
                        "environment": "testnet"
                    }
                ) as response:
                    response_time = time.time() - start_time
                    data = await response.json()
                    
                    if response.status == 200:
                        print(f"   ✅ 成功 ({response_time:.2f}s)")
                        response_text = data.get("response", "")
                        
                        # 检查是否包含治理相关信息
                        if any(keyword in response_text.lower() for keyword in ["治理", "governance", "提案", "proposal", "投票", "vote"]):
                            print(f"   🗳️  包含治理信息")
                            results.append(True)
                        else:
                            print(f"   ⚠️  未找到治理信息")
                            results.append(False)
                    else:
                        print(f"   ❌ 失败: HTTP {response.status}")
                        results.append(False)
            except Exception as e:
                print(f"   ❌ 异常: {e}")
                results.append(False)
        
        return results
    
    async def test_advanced_functions(self):
        """测试高级功能"""
        print("\n🔍 测试高级功能...")
        
        tests = [
            {
                "name": "跨链功能",
                "message": "请说明Injective的跨链功能",
                "session_id": "advanced_test_1"
            },
            {
                "name": "智能合约",
                "message": "请解释如何在Injective上部署智能合约",
                "session_id": "advanced_test_2"
            },
            {
                "name": "衍生品交易",
                "message": "请查询可用的衍生品市场",
                "session_id": "advanced_test_3"
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
                        "agent_id": f"advanced_agent_{i}",
                        "agent_key": self.private_key,
                        "environment": "testnet"
                    }
                ) as response:
                    response_time = time.time() - start_time
                    data = await response.json()
                    
                    if response.status == 200:
                        print(f"   ✅ 成功 ({response_time:.2f}s)")
                        response_text = data.get("response", "")
                        
                        # 检查是否包含高级功能信息
                        if any(keyword in response_text.lower() for keyword in ["跨链", "cross-chain", "智能合约", "smart contract", "衍生品", "derivative"]):
                            print(f"   🔧 包含高级功能信息")
                            results.append(True)
                        else:
                            print(f"   ⚠️  未找到高级功能信息")
                            results.append(False)
                    else:
                        print(f"   ❌ 失败: HTTP {response.status}")
                        results.append(False)
            except Exception as e:
                print(f"   ❌ 异常: {e}")
                results.append(False)
        
        return results
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 真实私钥区块链功能测试")
        print("=" * 50)
        
        # 检查私钥配置
        if not self.check_private_key():
            print("❌ 私钥配置检查失败，停止测试")
            return False
        
        tests = [
            ("账户余额测试", self.test_account_balance),
            ("交易功能测试", self.test_trading_functions),
            ("质押功能测试", self.test_staking_functions),
            ("治理功能测试", self.test_governance_functions),
            ("高级功能测试", self.test_advanced_functions)
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
                all_results.append(success_count >= total_count * 0.7)  # 70%成功率
            else:
                print(f"   结果: {'✅ 通过' if result else '❌ 失败'}")
                all_results.append(result)
        
        # 生成报告
        self.generate_report(all_results, tests)
        
        return all_results
    
    def generate_report(self, results, tests):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 真实私钥测试报告")
        print("=" * 60)
        
        total_tests = len(tests)
        successful_tests = sum(results)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📋 总测试数: {total_tests}")
        print(f"✅ 成功测试: {successful_tests}")
        print(f"❌ 失败测试: {total_tests - successful_tests}")
        print(f"📈 成功率: {success_rate:.1f}%")
        
        print(f"\n🔑 私钥信息:")
        print(f"   账户地址: {self.account_address}")
        print(f"   私钥: {self.private_key[:8]}...")
        print(f"   网络: testnet")
        
        print("\n📋 详细结果:")
        for i, (test_name, _) in enumerate(tests):
            status = "✅ 通过" if results[i] else "❌ 失败"
            print(f"   {test_name}: {status}")
        
        if success_rate >= 70:
            print("\n🎉 真实私钥测试总体通过！")
            print("✅ 区块链功能正常工作")
        else:
            print("\n⚠️  部分测试失败，请检查私钥和网络配置")
        
        print("=" * 60)

async def main():
    """主函数"""
    print("🔑 Injective Agent API 真实私钥测试工具")
    print("=" * 50)
    
    async with RealPrivateKeyTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
