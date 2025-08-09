#!/usr/bin/env python3
"""
自动化测试脚本 - Injective Agent API
测试所有API端点的功能
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

class AgentAPITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_root_endpoint(self):
        """测试根端点"""
        print("🔍 测试根端点 (GET /)...")
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                data = await response.json()
                print(f"✅ 根端点测试成功")
                print(f"   状态码: {response.status}")
                print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return True
        except Exception as e:
            print(f"❌ 根端点测试失败: {e}")
            return False
    
    async def test_ping_endpoint(self):
        """测试健康检查端点"""
        print("\n🔍 测试健康检查端点 (GET /ping)...")
        try:
            async with self.session.get(f"{self.base_url}/ping") as response:
                data = await response.json()
                print(f"✅ 健康检查测试成功")
                print(f"   状态码: {response.status}")
                print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return True
        except Exception as e:
            print(f"❌ 健康检查测试失败: {e}")
            return False
    
    async def test_chat_endpoint(self):
        """测试聊天端点"""
        print("\n🔍 测试聊天端点 (POST /chat)...")
        
        # 测试用例
        test_cases = [
            {
                "name": "基础聊天测试",
                "data": {
                    "message": "你好，请介绍一下你自己",
                    "session_id": "test_session_1",
                    "agent_id": "test_agent_1",
                    "agent_key": "default",
                    "environment": "testnet"
                }
            },
            {
                "name": "区块链功能测试",
                "data": {
                    "message": "请告诉我Injective区块链的主要功能",
                    "session_id": "test_session_2",
                    "agent_id": "test_agent_2",
                    "agent_key": "default",
                    "environment": "testnet"
                }
            },
            {
                "name": "错误处理测试",
                "data": {
                    "message": "",
                    "session_id": "test_session_3"
                }
            }
        ]
        
        results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n   测试 {i}: {test_case['name']}")
            try:
                async with self.session.post(
                    f"{self.base_url}/chat",
                    json=test_case['data']
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
    
    async def test_history_endpoint(self):
        """测试历史记录端点"""
        print("\n🔍 测试历史记录端点 (GET /history)...")
        
        test_sessions = ["test_session_1", "test_session_2", "default"]
        results = []
        
        for session_id in test_sessions:
            print(f"   测试会话: {session_id}")
            try:
                async with self.session.get(
                    f"{self.base_url}/history?session_id={session_id}"
                ) as response:
                    data = await response.json()
                    print(f"   ✅ 历史记录测试成功")
                    print(f"      状态码: {response.status}")
                    print(f"      响应: {json.dumps(data, indent=4, ensure_ascii=False)}")
                    results.append(True)
            except Exception as e:
                print(f"   ❌ 历史记录测试失败: {e}")
                results.append(False)
        
        return all(results)
    
    async def test_clear_endpoint(self):
        """测试清除历史记录端点"""
        print("\n🔍 测试清除历史记录端点 (POST /clear)...")
        
        test_sessions = ["test_session_1", "test_session_2"]
        results = []
        
        for session_id in test_sessions:
            print(f"   清除会话: {session_id}")
            try:
                async with self.session.post(
                    f"{self.base_url}/clear?session_id={session_id}"
                ) as response:
                    data = await response.json()
                    print(f"   ✅ 清除历史记录测试成功")
                    print(f"      状态码: {response.status}")
                    print(f"      响应: {json.dumps(data, indent=4, ensure_ascii=False)}")
                    results.append(True)
            except Exception as e:
                print(f"   ❌ 清除历史记录测试失败: {e}")
                results.append(False)
        
        return all(results)
    
    async def test_server_connectivity(self):
        """测试服务器连接性"""
        print("🔍 测试服务器连接性...")
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    print("✅ 服务器连接正常")
                    return True
                else:
                    print(f"❌ 服务器响应异常，状态码: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ 无法连接到服务器: {e}")
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始自动化测试 Injective Agent API")
        print("=" * 50)
        
        # 测试服务器连接性
        if not await self.test_server_connectivity():
            print("❌ 服务器连接失败，停止测试")
            return False
        
        print("\n" + "=" * 50)
        
        # 运行所有测试
        tests = [
            ("根端点", self.test_root_endpoint),
            ("健康检查", self.test_ping_endpoint),
            ("聊天功能", self.test_chat_endpoint),
            ("历史记录", self.test_history_endpoint),
            ("清除历史", self.test_clear_endpoint),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n📋 运行测试: {test_name}")
            result = await test_func()
            results.append((test_name, result))
        
        # 输出测试结果摘要
        print("\n" + "=" * 50)
        print("📊 测试结果摘要:")
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
            print("🎉 所有测试通过！Agent API 运行正常")
        else:
            print("⚠️  部分测试失败，请检查服务器状态")
        
        return passed == total

async def main():
    """主函数"""
    print("🤖 Injective Agent API 自动化测试工具")
    print("=" * 50)
    
    # 检查服务器是否运行
    print("正在检查服务器状态...")
    
    async with AgentAPITester() as tester:
        success = await tester.run_all_tests()
        
        if success:
            print("\n🎯 测试完成！Agent服务器运行正常")
        else:
            print("\n⚠️  测试完成，发现问题，请检查服务器配置")

if __name__ == "__main__":
    asyncio.run(main())
