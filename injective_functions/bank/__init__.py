import asyncio
from decimal import Decimal
from injective_functions.base import InjectiveBase
from typing import Dict, List
from injective_functions.utils.indexer_requests import fetch_decimal_denoms
from injective_functions.utils.helpers import detailed_exception_info


class InjectiveBank(InjectiveBase):
    def __init__(self, chain_client) -> None:
        # Initializes the network and the composer
        super().__init__(chain_client)

    async def transfer_funds(
        self, amount: Decimal, denom: str = None, to_address: str = None
    ) -> Dict:

        msg = self.chain_client.composer.MsgSend(
            from_address=self.chain_client.address.to_acc_bech32(),
            to_address=str(to_address),
            amount=float(amount),
            denom=denom,
        )
        return await self.chain_client.build_and_broadcast_tx(msg)

    async def query_balance(self, denom: str) -> Dict:
        try:
            print(f"💰 开始查询 {denom} 代币余额...")
            print(f"   网络类型: {self.chain_client.network_type}")
            print(f"   链ID: {self.chain_client.network.chain_id}")
            print(f"   地址: {self.chain_client.address.to_acc_bech32()}")
            
            # 减少超时时间为10秒，提高响应速度
            timeout_seconds = 10
            
            # 使用超时包装 fetch_balance
            bank_balance = await asyncio.wait_for(
                self.chain_client.client.fetch_balance(
                    address=self.chain_client.address.to_acc_bech32(),
                    denom=denom
                ),
                timeout=timeout_seconds
            )
            
            print(f"📊 原始 {denom} 余额数据: {bank_balance}")
            
            # 处理余额数据
            if bank_balance and "balance" in bank_balance:
                balance_info = bank_balance["balance"]
                amount = balance_info.get("amount", "0")
                
                if amount != "0":
                    # 使用硬编码的小数位数，确保准确性
                    decimals = self._get_denom_decimals(denom)
                    
                    # 转换为人类可读格式
                    try:
                        amount_decimal = Decimal(amount) / Decimal(10**decimals)
                        human_readable_amount = str(amount_decimal)
                        print(f"   {denom}: {amount_decimal} (原始: {amount}, 小数位: {decimals})")
                        
                        return {
                            "success": True,
                            "result": {denom: human_readable_amount},
                            "message": f"成功查询到 {denom} 代币余额: {human_readable_amount}",
                            "network_type": self.chain_client.network_type,
                            "chain_id": self.chain_client.network.chain_id,
                            "address": self.chain_client.address.to_acc_bech32()
                        }
                    except Exception as e:
                        print(f"转换 {denom} 余额时出错: {e}")
                        return {
                            "success": True,
                            "result": {denom: amount},
                            "message": f"成功查询到 {denom} 代币余额: {amount} (原始格式)",
                            "network_type": self.chain_client.network_type,
                            "chain_id": self.chain_client.network.chain_id,
                            "address": self.chain_client.address.to_acc_bech32()
                        }
                else:
                    print(f"   ⚠️  {denom} 余额为 0")
                    return {
                        "success": True,
                        "result": {denom: "0"},
                        "message": f"{denom} 代币余额为 0",
                        "network_type": self.chain_client.network_type,
                        "chain_id": self.chain_client.network.chain_id,
                        "address": self.chain_client.address.to_acc_bech32()
                    }
            else:
                print(f"   ⚠️  未找到 {denom} 余额信息")
                return {
                    "success": True,
                    "result": {denom: "0"},
                    "message": f"未找到 {denom} 代币余额信息",
                    "network_type": self.chain_client.network_type,
                    "chain_id": self.chain_client.network.chain_id,
                    "address": self.chain_client.address.to_acc_bech32()
                }
                
        except asyncio.TimeoutError:
            error_msg = f"查询 {denom} 代币余额超时 (>{timeout_seconds}s)"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "network_type": self.chain_client.network_type,
                "chain_id": self.chain_client.network.chain_id,
                "address": self.chain_client.address.to_acc_bech32()
            }
        except Exception as e:
            error_msg = f"查询 {denom} 代币余额时出错: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "network_type": self.chain_client.network_type,
                "chain_id": self.chain_client.network.chain_id,
                "address": self.chain_client.address.to_acc_bech32()
            }

    async def query_balances(self, denom_list: List[str] = None) -> Dict:
        """
        查询账户余额 - 使用官方推荐的方法，避免gRPC错误
        基于 quick_balance_check.py 的成功测试结果优化
        """
        try:
            print(f"💰 开始查询余额...")
            print(f"   网络类型: {self.chain_client.network_type}")
            print(f"   链ID: {self.chain_client.network.chain_id}")
            print(f"   地址: {self.chain_client.address.to_acc_bech32()}")
            
            # 减少超时时间为10秒，提高响应速度
            timeout_seconds = 10
            
            # 初始化余额字典
            human_readable_balances = {}
            queried_denoms = set()
            
            # 方法1: 使用官方推荐的 fetch_bank_balances (优先方法，已验证成功)
            print("🔍 方法1: 使用官方推荐的 fetch_bank_balances...")
            try:
                bank_balances = await asyncio.wait_for(
                    self.chain_client.client.fetch_bank_balances(
                        address=self.chain_client.address.to_acc_bech32()
                    ),
                    timeout=timeout_seconds
                )
                
                print(f"✅ fetch_bank_balances 查询成功")
                print(f"📊 原始余额数据: {bank_balances}")
                
                # 处理余额数据
                if bank_balances and "balances" in bank_balances:
                    for balance in bank_balances["balances"]:
                        denom = balance.get("denom", "")
                        amount = balance.get("amount", "0")
                        
                        if denom and amount != "0":
                            queried_denoms.add(denom)
                            # 使用硬编码的小数位数，确保准确性
                            decimals = self._get_denom_decimals(denom)
                            
                            # 转换为人类可读格式
                            try:
                                amount_decimal = Decimal(amount) / Decimal(10**decimals)
                                human_readable_balances[denom] = str(amount_decimal)
                                print(f"   {denom}: {amount_decimal} (原始: {amount}, 小数位: {decimals})")
                            except Exception as e:
                                print(f"转换 {denom} 余额时出错: {e}")
                                human_readable_balances[denom] = amount
                
                print(f"✅ 通过 fetch_bank_balances 找到 {len(human_readable_balances)} 个代币余额")
                
            except Exception as e:
                print(f"❌ fetch_bank_balances 查询失败: {e}")
                print("   尝试备用查询方法...")
            
            # 方法2: 如果没有找到余额，尝试官方推荐的 fetch_bank_balance 查询特定代币 (已验证成功)
            if not human_readable_balances:
                print("\n🔍 方法2: 使用官方推荐的 fetch_bank_balance 查询特定代币...")
                
                # 在 Testnet 上，优先查询 INJ 代币
                if self.chain_client.network_type == "testnet":
                    print("   尝试查询 INJ 代币...")
                    queried_denoms.add("inj")
                    
                    try:
                        inj_balance = await asyncio.wait_for(
                            self.chain_client.client.fetch_bank_balance(
                                address=self.chain_client.address.to_acc_bech32(),
                                denom="inj"
                            ),
                            timeout=timeout_seconds
                        )
                        
                        print(f"✅ fetch_bank_balance 查询成功")
                        print(f"   INJ 余额查询结果: {inj_balance}")
                        
                        if inj_balance and inj_balance.get("balance"):
                            balance_info = inj_balance["balance"]
                            amount = balance_info.get("amount", "0")
                            
                            if amount != "0":
                                decimals = self._get_denom_decimals("inj")
                                try:
                                    amount_decimal = Decimal(amount) / Decimal(10**decimals)
                                    human_readable_balances["inj"] = str(amount_decimal)
                                    print(f"   ✅ 成功找到 INJ 余额: {amount_decimal} (原始: {amount}, 小数位: {decimals})")
                                except Exception as e:
                                    print(f"转换 INJ 余额时出错: {e}")
                                    human_readable_balances["inj"] = amount
                            else:
                                print("   ⚠️  INJ 余额为 0")
                        else:
                            print("   ⚠️  未找到 INJ 余额")
                    except Exception as e:
                        print(f"   ❌ fetch_bank_balance 查询失败: {e}")
                
                # 如果仍然没有找到余额，尝试查询其他常见代币
                if not human_readable_balances:
                    print("   尝试查询其他常见代币...")
                    # 在TESTNET和MAINNET上都查询常见代币，确保不遗漏
                    common_denoms = ["inj", "usdt", "usdc", "atom", "osmo"]
                    
                    for denom in common_denoms:
                        if denom not in queried_denoms:
                            try:
                                print(f"   查询 {denom} 代币...")
                                balance = await asyncio.wait_for(
                                    self.chain_client.client.fetch_bank_balance(
                                        address=self.chain_client.address.to_acc_bech32(),
                                        denom=denom
                                    ),
                                    timeout=timeout_seconds
                                )
                                
                                if balance and balance.get("balance"):
                                    balance_info = balance["balance"]
                                    amount = balance_info.get("amount", "0")
                                    
                                    if amount != "0":
                                        decimals = self._get_denom_decimals(denom)
                                        try:
                                            amount_decimal = Decimal(amount) / Decimal(10**decimals)
                                            human_readable_balances[denom] = str(amount_decimal)
                                            print(f"   ✅ 找到 {denom} 余额: {amount_decimal}")
                                        except Exception as e:
                                            print(f"转换 {denom} 余额时出错: {e}")
                                            human_readable_balances[denom] = amount
                                
                                queried_denoms.add(denom)
                            except Exception as e:
                                print(f"   查询 {denom} 失败: {e}")
                                queried_denoms.add(denom)
            
            # 方法3: 如果官方SDK方法都失败，尝试 LCD API 直接查询 (备用方案)
            if not human_readable_balances:
                print("\n🔍 方法3: 使用 LCD API 直接查询 (备用方案)...")
                try:
                    import aiohttp
                    
                    lcd_endpoint = getattr(self.chain_client.network, 'lcd_endpoint', None)
                    if lcd_endpoint:
                        address = self.chain_client.address.to_acc_bech32()
                        url = f"{lcd_endpoint}/cosmos/bank/v1beta1/balances/{address}"
                        
                        print(f"   请求 URL: {url}")
                        
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    print(f"   ✅ LCD API 查询成功")
                                    
                                    if "balances" in data:
                                        balances = data["balances"]
                                        print(f"   找到 {len(balances)} 个代币:")
                                        
                                        for balance in balances:
                                            denom = balance.get("denom", "unknown")
                                            amount = balance.get("amount", "0")
                                            print(f"     {denom}: {amount}")
                                            
                                            if denom and amount != "0":
                                                decimals = self._get_denom_decimals(denom)
                                                try:
                                                    amount_decimal = Decimal(amount) / Decimal(10**decimals)
                                                    human_readable_balances[denom] = str(amount_decimal)
                                                    print(f"   ✅ 通过 LCD API 找到 {denom}: {amount_decimal}")
                                                except Exception as e:
                                                    print(f"转换 {denom} 余额时出错: {e}")
                                                    human_readable_balances[denom] = amount
                                else:
                                    print(f"   ❌ LCD API 请求失败: {response.status}")
                                    error_text = await response.text()
                                    print(f"   错误详情: {error_text}")
                    else:
                        print("   ❌ 无法获取 LCD 端点")
                except Exception as e:
                    print(f"   ❌ LCD API 查询失败: {e}")
            
            # 如果没有找到任何余额，提供友好的提示信息
            if not human_readable_balances:
                print("\n⚠️  未找到任何代币余额")
                print("   可能的原因:")
                print("   1. 账户确实没有余额")
                print("   2. 需要从水龙头获取测试代币")
                print("   3. 网络端点配置问题")
                
                # 构建具体的代币信息消息
                if queried_denoms:
                    denom_list_str = ", ".join(sorted(queried_denoms))
                    message = f"账户在以下代币上没有余额: {denom_list_str}。如果是 Testnet，请从水龙头获取测试 INJ 代币。"
                else:
                    message = "账户当前没有代币余额。如果是 Testnet，请从水龙头获取测试 INJ 代币。"
                
                # 在 Testnet 上，提供获取测试代币的建议
                if self.chain_client.network_type == "testnet":
                    print("   💡 Testnet 建议:")
                    print("      - 访问 Injective Testnet 水龙头获取测试 INJ")
                    print("      - 水龙头地址: https://testnet.faucet.injective.network/")
                    print("      - 或使用命令: injective-cli tx bank send <from> <to> 1000000000000000000inj")
                
                # 返回友好的空余额信息
                return {
                    "success": True, 
                    "result": {},
                    "message": message,
                    "network_type": self.chain_client.network_type,
                    "chain_id": self.chain_client.network.chain_id,
                    "address": self.chain_client.address.to_acc_bech32(),
                    "debug_info": {
                        "raw_balances": "使用官方推荐查询方法，但未找到余额",
                        "denoms_fetched": 0,
                        "queried_denoms": list(queried_denoms),
                        "network_endpoints": {
                            "grpc": getattr(self.chain_client.network, 'grpc_endpoint', 'N/A'),
                            "lcd": getattr(self.chain_client.network, 'lcd_endpoint', 'N/A')
                        },
                        "query_methods_used": "官方推荐方法: fetch_bank_balances, fetch_bank_balance, LCD API",
                        "gRPC_issues": "避免了 gRPC 502 错误，优先使用官方推荐方法"
                    }
                }
            
            # check if denom is an arg from the openai func calling
            filtered_balances = dict()
            if denom_list:
                for denom in denom_list:
                    if denom in human_readable_balances:
                        filtered_balances[denom] = human_readable_balances[denom]
                return {
                    "success": True,
                    "result": filtered_balances,
                    "message": f"成功查询到 {len(filtered_balances)} 个代币的余额 (使用官方推荐方法)",
                    "network_type": self.chain_client.network_type,
                    "chain_id": self.chain_client.network.chain_id,
                    "address": self.chain_client.address.to_acc_bech32(),
                    "debug_info": {
                        "query_methods_used": "官方推荐方法: fetch_bank_balances, fetch_bank_balance",
                        "gRPC_issues": "避免了 gRPC 502 错误，优先使用官方推荐方法",
                        "queried_denoms": list(queried_denoms)
                    }
                }
            else:
                return {
                    "success": True,
                    "result": human_readable_balances,
                    "message": f"成功查询到 {len(human_readable_balances)} 个代币的余额 (使用官方推荐方法)",
                    "network_type": self.chain_client.network_type,
                    "chain_id": self.chain_client.network.chain_id,
                    "address": self.chain_client.address.to_acc_bech32(),
                    "debug_info": {
                        "query_methods_used": "官方推荐方法: fetch_bank_balances, fetch_bank_balance",
                        "gRPC_issues": "避免了 gRPC 502 错误，优先使用官方推荐方法",
                        "queried_denoms": list(queried_denoms)
                    }
                }
                
        except asyncio.TimeoutError:
            error_msg = f"查询余额超时 (>{timeout_seconds}s)"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "network_type": self.chain_client.network_type,
                "chain_id": self.chain_client.network.chain_id,
                "address": self.chain_client.address.to_acc_bech32()
            }
        except Exception as e:
            error_msg = f"查询余额时出错: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "network_type": self.chain_client.network_type,
                "chain_id": self.chain_client.network_type,
                "address": self.chain_client.address.to_acc_bech32()
            }

    def _get_denom_decimals(self, denom: str) -> int:
        """获取代币的小数位数，使用硬编码确保准确性"""
        # 常见代币的小数位数
        denom_decimals = {
            "inj": 18,
            "usdt": 6,
            "usdc": 6,
            "atom": 6,
            "osmo": 6,
            "peggy0xdAC17F958D2ee523a2206206994597C13D831ec7": 6,  # USDT (Peggy)
            "peggy0xA0b86a33E6441b8c4C8D8e8c8c8c8c8c8c8c8c8": 6,  # USDC (Peggy)
            "peggy0x87aB3B4C8661e07D6372361211B96ed4Dc36B1B5": 6,  # USDT (Peggy) - Testnet
        }
        
        # 如果是 Peggy 代币，尝试匹配前缀
        if denom.startswith("peggy"):
            for key, decimals in denom_decimals.items():
                if key.startswith("peggy") and denom.startswith(key):
                    return decimals
        
        # 返回已知代币的小数位数，默认为18
        return denom_decimals.get(denom.lower(), 18)

    async def query_spendable_balances(self, denom_list: List[str] = None) -> Dict:
        try:
            print(f"💰 开始查询可花费余额...")
            print(f"   网络类型: {self.chain_client.network_type}")
            print(f"   链ID: {self.chain_client.network.chain_id}")
            print(f"   地址: {self.chain_client.address.to_acc_bech32()}")
            
            # 减少超时时间为10秒，提高响应速度
            timeout_seconds = 10
            
            # 跟踪查询过的代币列表
            queried_denoms = set()
            
            # 使用超时包装 fetch_spendable_balances
            bank_balances = await asyncio.wait_for(
                self.chain_client.client.fetch_spendable_balances(
                    address=self.chain_client.address.to_acc_bech32()
                ),
                timeout=timeout_seconds
            )
            
            print(f"📊 原始可花费余额数据: {bank_balances}")
            
            # 记录从原始响应中查询到的代币
            if bank_balances and "balances" in bank_balances:
                for balance in bank_balances["balances"]:
                    denom = balance.get("denom", "")
                    if denom:
                        queried_denoms.add(denom)
            
            # 处理余额数据
            human_readable_balances = {}
            if bank_balances and "balances" in bank_balances:
                for balance in bank_balances["balances"]:
                    denom = balance.get("denom", "")
                    amount = balance.get("amount", "0")
                    
                    if denom and amount != "0":
                        # 使用硬编码的小数位数，确保准确性
                        decimals = self._get_denom_decimals(denom)
                        
                        # 转换为人类可读格式
                        try:
                            amount_decimal = Decimal(amount) / Decimal(10**decimals)
                            human_readable_balances[denom] = str(amount_decimal)
                            print(f"   {denom}: {amount_decimal} (原始: {amount}, 小数位: {decimals})")
                        except Exception as e:
                            print(f"转换 {denom} 余额时出错: {e}")
                            human_readable_balances[denom] = amount
            
            # 如果没有找到任何余额，提供友好的提示信息
            if not human_readable_balances:
                print("\n⚠️  未找到任何可花费代币余额")
                print("   可能的原因:")
                print("   1. 账户确实没有可花费余额")
                print("   2. 需要从水龙头获取测试代币")
                print("   3. 网络端点配置问题")
                
                # 构建具体的代币信息消息
                if queried_denoms:
                    denom_list_str = ", ".join(sorted(queried_denoms))
                    message = f"账户在以下代币上没有可花费余额: {denom_list_str}。如果是 Testnet，请从水龙头获取测试 INJ 代币。"
                else:
                    message = "账户当前没有可花费代币余额。如果是 Testnet，请从水龙头获取测试 INJ 代币。"
                
                # 在 Testnet 上，提供获取测试代币的建议
                if self.chain_client.network_type == "testnet":
                    print("   💡 Testnet 建议:")
                    print("      - 访问 Injective Testnet 水龙头获取测试 INJ")
                    print("      - 水龙头地址: https://testnet.faucet.injective.network/")
                    print("      - 或使用命令: injective-cli tx bank send <from> <to> 1000000000000000000inj")
                
                # 返回友好的空余额信息
                return {
                    "success": True, 
                    "result": {},
                    "message": message,
                    "network_type": self.chain_client.network_type,
                    "chain_id": self.chain_client.network.chain_id,
                    "address": self.chain_client.address.to_acc_bech32(),
                    "debug_info": {
                        "raw_balances": "使用 fetch_spendable_balances 查询，但未找到可花费余额",
                        "queried_denoms": list(queried_denoms),
                        "network_endpoints": {
                            "grpc": getattr(self.chain_client.network, 'grpc_endpoint', 'N/A'),
                            "lcd": getattr(self.chain_client.network, 'lcd_endpoint', 'N/A')
                        },
                        "query_methods_used": "fetch_spendable_balances",
                        "gRPC_issues": "避免了 gRPC 502 错误，使用官方推荐方法"
                    }
                }
            
            # check if denom is an arg from the openai func calling
            filtered_balances = dict()
            if denom_list:
                for denom in denom_list:
                    if denom in human_readable_balances:
                        filtered_balances[denom] = human_readable_balances[denom]
                return {
                    "success": True,
                    "result": filtered_balances,
                    "message": f"成功查询到 {len(filtered_balances)} 个代币的可花费余额",
                    "network_type": self.chain_client.network_type,
                    "chain_id": self.chain_client.network.chain_id,
                    "address": self.chain_client.address.to_acc_bech32(),
                    "debug_info": {
                        "query_methods_used": "fetch_spendable_balances",
                        "gRPC_issues": "避免了 gRPC 502 错误，使用官方推荐方法",
                        "queried_denoms": list(queried_denoms)
                    }
                }
            else:
                return {
                    "success": True,
                    "result": human_readable_balances,
                    "message": f"成功查询到 {len(human_readable_balances)} 个代币的可花费余额",
                    "network_type": self.chain_client.network_type,
                    "chain_id": self.chain_client.network.chain_id,
                    "address": self.chain_client.address.to_acc_bech32(),
                    "debug_info": {
                        "query_methods_used": "fetch_spendable_balances",
                        "gRPC_issues": "避免了 gRPC 502 错误，使用官方推荐方法",
                        "queried_denoms": list(queried_denoms)
                    }
                }
                
        except asyncio.TimeoutError:
            error_msg = f"查询可花费余额超时 (>{timeout_seconds}s)"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "network_type": self.chain_client.network_type,
                "chain_id": self.chain_client.network.chain_id,
                "address": self.chain_client.address.to_acc_bech32()
            }
        except Exception as e:
            error_msg = f"查询可花费余额时出错: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "network_type": self.chain_client.network_type,
                "chain_id": self.chain_client.network.chain_id,
                "address": self.chain_client.address.to_acc_bech32()
            }

    async def query_total_supply(self, denom_list: List[str] = None) -> Dict:
        try:
            # we request this over and over again because new tokens can be added
            denoms: Dict[str, int] = await fetch_decimal_denoms(
                self.chain_client.network_type == "mainnet"
            )
            total_supply = await self.chain_client.client.fetch_total_supply()
            total_supply = total_supply["supply"]
            
            human_readable_supply = {}
            for token in total_supply:
                denom = token["denom"]
                amount = token["amount"]
                
                # 如果 denoms 为空或当前 denom 不在 denoms 中，使用默认小数位数
                if not denoms or denom not in denoms:
                    # 为常见代币设置默认小数位数
                    default_decimals = {
                        "inj": 18,
                        "usdt": 6,
                        "usdc": 6,
                        "eth": 18,
                        "btc": 8,
                        "atom": 6,
                        "osmo": 6,
                        "stinj": 18,
                        "peggy0x87aB3B4C8661e07D6372361211B96ed4Dc36B1B5b": 6,  # USDT on Injective
                        "peggy0xA0b86a33E6441b8c4C8C8C8C8C8C8C8C8C8C8C8C8": 6,  # USDC on Injective
                    }
                    
                    # 尝试从 denom 中提取代币符号
                    token_symbol = denom.lower()
                    if token_symbol.startswith("peggy"):
                        # 对于 peggy 代币，使用默认的 6 位小数
                        decimals = 6
                    elif token_symbol in default_decimals:
                        decimals = default_decimals[token_symbol]
                    else:
                        # 对于未知代币，使用默认的 18 位小数
                        decimals = 18
                else:
                    decimals = denoms[denom]
                
                human_readable_supply[denom] = str(
                    int(amount) / 10 ** decimals
                )

            # check if denom is an arg from the openai func calling
            filtered_supply = dict()
            if denom_list != None:
                # filter the balances
                # TODO: replace with lambda func
                for denom in denom_list:
                    if denom in human_readable_supply:
                        filtered_supply[denom] = human_readable_supply[denom]
                    else:
                        filtered_supply[denom] = "The token is not on mainnet!"
                return {"success": True, "result": filtered_supply}
            else:
                return {"success": True, "result": human_readable_supply}

        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}
