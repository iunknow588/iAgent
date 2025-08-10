#!/usr/bin/env python3
"""
调试余额查询脚本 - 测试不同的查询方法
"""

import asyncio
import aiohttp
from pyinjective.core.network import Network
from pyinjective.async_client import AsyncClient
from pyinjective.async_client_v2 import AsyncClient as AsyncClientV2

async def test_direct_api():
    """直接调用 API 查询余额"""
    print("🔍 测试直接 API 调用...")
    address = "inj1m9wzsyx0ksaauj0a59gmzlnnyzyakawh3aa5xw"
    
    async with aiohttp.ClientSession() as session:
        url = f"https://testnet.sentry.lcd.injective.network:443/cosmos/bank/v1beta1/balances/{address}"
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"✅ 直接 API 调用成功")
                print(f"   余额数量: {len(data.get('balances', []))}")
                for balance in data.get('balances', []):
                    print(f"   {balance.get('denom')}: {balance.get('amount')}")
                return data
            else:
                print(f"❌ 直接 API 调用失败: {resp.status}")
                return None

async def test_sdk_v1():
    """测试 SDK V1 客户端"""
    print("\n🔍 测试 SDK V1 客户端...")
    try:
        network = Network.testnet()
        client = AsyncClient(network)
        
        address = "inj1m9wzsyx0ksaauj0a59gmzlnnyzyakawh3aa5xw"
        bank_balances = await client.fetch_bank_balances(address=address)
        
        print(f"✅ SDK V1 查询成功")
        print(f"   数据类型: {type(bank_balances)}")
        print(f"   内容: {bank_balances}")
        
        if isinstance(bank_balances, dict) and "balances" in bank_balances:
            balances = bank_balances["balances"]
            print(f"   余额数量: {len(balances)}")
            for balance in balances:
                print(f"   {balance.get('denom')}: {balance.get('amount')}")
        
        return bank_balances
        
    except Exception as e:
        print(f"❌ SDK V1 查询失败: {e}")
        return None

async def test_sdk_v2():
    """测试 SDK V2 客户端"""
    print("\n🔍 测试 SDK V2 客户端...")
    try:
        network = Network.testnet()
        client = AsyncClientV2(network)
        
        address = "inj1m9wzsyx0ksaauj0a59gmzlnnyzyakawh3aa5xw"
        bank_balances = await client.fetch_bank_balances(address=address)
        
        print(f"✅ SDK V2 查询成功")
        print(f"   数据类型: {type(bank_balances)}")
        print(f"   内容: {bank_balances}")
        
        if hasattr(bank_balances, 'balances'):
            balances = bank_balances.balances
            print(f"   余额数量: {len(balances)}")
            for balance in balances:
                print(f"   {balance.denom}: {balance.amount}")
        
        return bank_balances
        
    except Exception as e:
        print(f"❌ SDK V2 查询失败: {e}")
        return None

async def main():
    """主函数"""
    print("🚀 余额查询调试工具")
    print("=" * 50)
    
    # 测试直接 API 调用
    direct_result = await test_direct_api()
    
    # 测试 SDK V1 客户端
    v1_result = await test_sdk_v1()
    
    # 测试 SDK V2 客户端
    v2_result = await test_sdk_v2()
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"   直接 API: {'✅ 成功' if direct_result else '❌ 失败'}")
    print(f"   SDK V1:  {'✅ 成功' if v1_result else '❌ 失败'}")
    print(f"   SDK V2:  {'✅ 成功' if v2_result else '❌ 失败'}")
    
    if direct_result and not v1_result and not v2_result:
        print("\n💡 问题分析:")
        print("   直接 API 调用成功，但 SDK 调用失败")
        print("   可能是 SDK 版本兼容性问题或网络配置问题")
    
    print("=" * 50)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，退出程序")
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc()
