#!/usr/bin/env python3
"""
快速余额查询脚本 - 基于 Injective Python SDK
读取.env环境变量中的账户信息并查询余额
"""

import asyncio
import json
import os
from decimal import Decimal
from typing import Dict, List, Optional
from dotenv import load_dotenv

# 导入必要的模块 - 使用正确的导入路径
try:
    from pyinjective.core.network import Network
    from pyinjective.async_client import AsyncClient
    from pyinjective.async_client_v2 import AsyncClient as AsyncClientV2
    from pyinjective.wallet import Address, PrivateKey
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请安装 pyinjective: pip install injective-py")
    exit(1)

class QuickBalanceChecker:
    def __init__(self, network_type: str = "testnet"):
        """
        初始化余额查询器
        
        Args:
            network_type: 网络类型 ("testnet" 或 "mainnet")
        """
        self.network_type = network_type
        self.network = Network.testnet() if network_type == "testnet" else Network.mainnet()
        
        # 使用 V2 客户端以获得更好的兼容性
        self.client = AsyncClientV2(self.network)
        
        print(f"🔧 初始化 {network_type.upper()} 网络")
        print(f"   链ID: {self.network.chain_id}")
        print(f"   gRPC端点: {self.network.grpc_endpoint}")
        print(f"   LCD端点: {self.network.lcd_endpoint}")
    
    def _get_denom_decimals(self, denom: str) -> int:
        """获取代币的小数位数"""
        # 常见代币的小数位数
        denom_decimals = {
            "inj": 18,
            "usdt": 6,
            "usdc": 6,
            "atom": 6,
            "osmo": 6,
            "peggy0xdAC17F958D2ee523a2206206994597C13D831ec7": 6,  # USDT (Peggy)
            "peggy0xA0b86a33E6441b8c4C8D8e8c8c8c8c8c8c8c8c8": 6,  # USDC (Peggy)
            "peggy0x87aB3B4C8661e07D6372361211B96ed4Dc36B1B5": 6,  # USDT (Peggy) - 当前测试网代币
        }
        
        # 如果是 Peggy 代币，尝试匹配前缀
        if denom.startswith("peggy"):
            for key, decimals in denom_decimals.items():
                if key.startswith("peggy") and denom.startswith(key):
                    return decimals
        
        # 返回已知代币的小数位数，默认为18
        return denom_decimals.get(denom.lower(), 18)
    
    async def check_balance_with_address(self, address: str) -> Dict:
        """
        使用地址查询余额
        
        Args:
            address: 要查询的地址
            
        Returns:
            包含余额信息的字典
        """
        try:
            print(f"\n💰 查询地址余额: {address}")
            print(f"   网络: {self.network_type.upper()}")
            print(f"   链ID: {self.network.chain_id}")
            
            # 使用 V2 客户端的 fetch_bank_balances 方法
            print("\n🔍 查询银行模块余额...")
            try:
                bank_balances = await self.client.fetch_bank_balances(address=address)
                print(f"✅ 查询成功")
                
                # 处理 V2 客户端返回的数据（可能是字典格式）
                if bank_balances and isinstance(bank_balances, dict) and "balances" in bank_balances:
                    balances = bank_balances["balances"]
                    print(f"   找到 {len(balances)} 个代币余额")
                    
                    human_readable_balances = {}
                    for balance in balances:
                        denom = balance.get("denom", "")
                        amount = balance.get("amount", "0")
                        
                        if denom and amount != "0":
                            decimals = self._get_denom_decimals(denom)
                            try:
                                amount_decimal = Decimal(amount) / Decimal(10**decimals)
                                human_readable_balances[denom] = str(amount_decimal)
                                print(f"   {denom}: {amount_decimal} (原始: {amount}, 小数位: {decimals})")
                            except Exception as e:
                                print(f"转换 {denom} 余额时出错: {e}")
                                human_readable_balances[denom] = amount
                    
                    if human_readable_balances:
                        return {
                            "success": True,
                            "method": "fetch_bank_balances_v2",
                            "result": human_readable_balances,
                            "message": f"成功查询到 {len(human_readable_balances)} 个代币的余额",
                            "raw_data": str(bank_balances)
                        }
                    else:
                        print("   ⚠️  所有代币余额都为 0")
                # 处理 V2 客户端返回的对象格式（向后兼容）
                elif bank_balances and hasattr(bank_balances, 'balances'):
                    balances = bank_balances.balances
                    print(f"   找到 {len(balances)} 个代币余额")
                    
                    human_readable_balances = {}
                    for balance in balances:
                        denom = balance.denom
                        amount = balance.amount
                        
                        if denom and amount != "0":
                            decimals = self._get_denom_decimals(denom)
                            try:
                                amount_decimal = Decimal(amount) / Decimal(10**decimals)
                                human_readable_balances[denom] = str(amount_decimal)
                                print(f"   {denom}: {amount_decimal} (原始: {amount}, 小数位: {decimals})")
                            except Exception as e:
                                print(f"转换 {denom} 余额时出错: {e}")
                                human_readable_balances[denom] = amount
                    
                    if human_readable_balances:
                        return {
                            "success": True,
                            "method": "fetch_bank_balances_v2",
                            "result": human_readable_balances,
                            "message": f"成功查询到 {len(human_readable_balances)} 个代币的余额",
                            "raw_data": str(bank_balances)
                        }
                    else:
                        print("   ⚠️  所有代币余额都为 0")
                        
            except Exception as e:
                print(f"❌ V2 客户端查询失败: {e}")
                
                # 回退到 V1 客户端
                print("\n🔄 回退到 V1 客户端...")
                try:
                    v1_client = AsyncClient(self.network)
                    bank_balances = await v1_client.fetch_bank_balances(address=address)
                    print(f"✅ V1 客户端查询成功")
                    
                    if bank_balances and "balances" in bank_balances:
                        balances = bank_balances["balances"]
                        print(f"   找到 {len(balances)} 个代币余额")
                        
                        human_readable_balances = {}
                        for balance in balances:
                            denom = balance.get("denom", "")
                            amount = balance.get("amount", "0")
                            
                            if denom and amount != "0":
                                decimals = self._get_denom_decimals(denom)
                                try:
                                    amount_decimal = Decimal(amount) / Decimal(10**decimals)
                                    human_readable_balances[denom] = str(amount_decimal)
                                    print(f"   {denom}: {amount_decimal} (原始: {amount}, 小数位: {decimals})")
                                except Exception as e:
                                    print(f"转换 {denom} 余额时出错: {e}")
                                    human_readable_balances[denom] = amount
                        
                        if human_readable_balances:
                            return {
                                "success": True,
                                "method": "fetch_bank_balances_v1",
                                "result": human_readable_balances,
                                "message": f"成功查询到 {len(human_readable_balances)} 个代币的余额",
                                "raw_data": bank_balances
                            }
                        
                except Exception as v1_error:
                    print(f"❌ V1 客户端也失败: {v1_error}")
            
            # 如果没有找到任何余额
            print("\n⚠️  未找到任何代币余额")
            print("   可能的原因:")
            print("   1. 账户确实没有余额")
            print("   2. 需要从水龙头获取测试代币")
            print("   3. 网络端点配置问题")
            
            if self.network_type == "testnet":
                print("   💡 Testnet 建议:")
                print("      - 访问 Injective Testnet 水龙头获取测试 INJ")
                print("      - 水龙头地址: https://testnet.faucet.injective.network/")
            
            return {
                "success": True,
                "method": "none",
                "result": {},
                "message": "账户当前没有代币余额",
                "raw_data": None
            }
            
        except Exception as e:
            error_msg = f"查询余额时出错: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "method": "error"
            }
    
    async def check_balance_with_private_key(self, private_key_hex: str) -> Dict:
        """
        使用私钥查询余额
        
        Args:
            private_key_hex: 私钥的十六进制字符串
            
        Returns:
            包含余额信息的字典
        """
        try:
            # 从私钥创建地址
            private_key = PrivateKey.from_hex(private_key_hex)
            address = private_key.to_address()
            address_str = address.to_acc_bech32()
            
            print(f"🔑 从私钥创建地址: {address_str}")
            
            # 使用地址查询余额
            return await self.check_balance_with_address(address_str)
            
        except Exception as e:
            error_msg = f"从私钥创建地址时出错: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "method": "error"
            }

def load_environment_config() -> Dict[str, str]:
    """加载环境配置"""
    # 加载 .env 文件
    load_dotenv()
    
    config = {
        "network": os.getenv("NETWORK", "testnet"),
        "account_name": os.getenv("ACCOUNT_NAME", ""),
        "account_address": os.getenv("ACCOUNT_ADDRESS", ""),
        "private_key": os.getenv("PRIVATE_KEY", ""),
    }
    
    return config

async def main():
    """主函数"""
    print("🚀 Injective 快速余额查询工具")
    print("=" * 50)
    
    # 加载环境配置
    config = load_environment_config()
    
    print("📋 环境配置:")
    print(f"   网络: {config['network']}")
    print(f"   账户名称: {config['account_name']}")
    print(f"   账户地址: {config['account_address']}")
    print(f"   私钥: {'已配置' if config['private_key'] else '未配置'}")
    
    # 创建余额查询器
    checker = QuickBalanceChecker(config['network'])
    
    # 如果有账户地址，直接查询
    if config['account_address']:
        print(f"\n🔍 查询配置的账户地址: {config['account_address']}")
        result = await checker.check_balance_with_address(config['account_address'])
    elif config['private_key']:
        print(f"\n🔍 使用私钥查询余额...")
        result = await checker.check_balance_with_private_key(config['private_key'])
    else:
        print("\n⚠️  未找到账户配置信息")
        print("   请在 .env 文件中设置以下参数之一:")
        print("   - ACCOUNT_ADDRESS: 账户地址")
        print("   - PRIVATE_KEY: 私钥")
        
        # 使用示例地址进行演示
        demo_address = "inj1hkhdaj2a82clm7psndf0u9lndj7cdrlz8l7ee5"
        print(f"\n💡 使用示例地址进行演示: {demo_address}")
        result = await checker.check_balance_with_address(demo_address)
    
    # 显示结果
    print("\n" + "=" * 50)
    print("📊 查询结果:")
    print(f"   成功: {result.get('success', False)}")
    print(f"   方法: {result.get('method', 'unknown')}")
    
    if result.get('success'):
        if result.get('result'):
            print(f"   余额: {result['result']}")
        else:
            print("   余额: 无")
        print(f"   消息: {result.get('message', '')}")
    else:
        print(f"   错误: {result.get('error', 'unknown error')}")
    
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
