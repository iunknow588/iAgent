from grpc import RpcError
from pyinjective.async_client import AsyncClient
from pyinjective.constant import GAS_FEE_BUFFER_AMOUNT, GAS_PRICE
from pyinjective.core.network import Network
from pyinjective.core.broadcaster import MsgBroadcasterWithPk
from pyinjective.transaction import Transaction
from pyinjective.wallet import PrivateKey
from injective_functions.utils.helpers import detailed_exception_info
from network.connectivity import get_smart_endpoint


class ChainInteractor:
    def __init__(self, network_type: str = "mainnet", private_key: str = None) -> None:
        self.private_key = private_key
        self.network_type = network_type
        if not self.private_key:
            raise ValueError("No private key found in environment variables")

        # 使用全局可达性测试的最佳端点，而不是 pyinjective 默认端点
        self.network = self._create_custom_network()
        self.client = None
        self.composer = None
        self.message_broadcaster = None

        # Initialize account
        self.priv_key = PrivateKey.from_hex(self.private_key)
        self.pub_key = self.priv_key.to_public_key()
        self.address = self.pub_key.to_address()

    def _create_custom_network(self):
        """创建使用最佳端点的自定义网络配置"""
        try:
            # 获取经过可达性测试验证的最佳端点
            lcd_endpoint = get_smart_endpoint(self.network_type, "lcd")
            
            print(f"🔗 使用最佳端点配置:")
            print(f"   LCD: {lcd_endpoint}")
            print(f"   gRPC: 使用pyinjective默认配置")
            
            # 策略：使用pyinjective的默认Network配置，但手动替换LCD端点
            # 这样可以确保所有其他配置都是正确的
            if self.network_type == "testnet":
                network = Network.testnet()
                # 手动替换LCD端点
                network.lcd_endpoint = lcd_endpoint
                print(f"   ✅ 已替换LCD端点为: {lcd_endpoint}")
                return network
            else:
                network = Network.mainnet()
                # 手动替换LCD端点
                network.lcd_endpoint = lcd_endpoint
                print(f"   ✅ 已替换LCD端点为: {lcd_endpoint}")
                return network
        except Exception as e:
            print(f"⚠️  无法获取最佳端点，使用默认配置: {e}")
            # 回退到默认配置
            return Network.testnet() if self.network_type == "testnet" else Network.mainnet()

    async def init_client(self):
        """Initialize the Injective client and required components"""
        try:
            print(f"🔌 初始化 Injective 客户端...")
            print(f"   网络类型: {self.network_type}")
            print(f"   链ID: {self.network.chain_id}")
            print(f"   LCD端点: {self.network.lcd_endpoint}")
            print(f"   gRPC端点: {self.network.grpc_endpoint}")
            
            self.client = AsyncClient(self.network)
            self.composer = await self.client.composer()
            await self.client.sync_timeout_height()
            await self.client.fetch_account(self.address.to_acc_bech32())
            self.message_broadcaster = MsgBroadcasterWithPk.new_using_simulation(
                network=self.network, private_key=self.private_key
            )
            print("✅ Injective 客户端初始化成功")
        except Exception as e:
            print(f"❌ Injective 客户端初始化失败: {str(e)}")
            raise e

    async def build_and_broadcast_tx(self, msg):
        """Common function to build and broadcast transactions"""
        try:
            # 确保客户端已初始化
            if not self.client:
                await self.init_client()
                
            tx = (
                Transaction()
                .with_messages(msg)
                .with_sequence(self.client.get_sequence())
                .with_account_num(self.client.get_number())
                .with_chain_id(self.network.chain_id)
            )

            sim_sign_doc = tx.get_sign_doc(self.pub_key)
            sim_sig = self.priv_key.sign(sim_sign_doc.SerializeToString())
            sim_tx_raw_bytes = tx.get_tx_data(sim_sig, self.pub_key)

            try:
                sim_res = await self.client.simulate(sim_tx_raw_bytes)
            except RpcError as ex:
                return {"success": False, "error": f"Simulation failed: {str(ex)}"}

            gas_price = GAS_PRICE
            gas_limit = (
                int(sim_res["gasInfo"]["gasUsed"]) + int(2) * GAS_FEE_BUFFER_AMOUNT
            )
            gas_fee = "{:.18f}".format((gas_price * gas_limit) / pow(10, 18)).rstrip(
                "0"
            )

            fee = [
                self.composer.coin(
                    amount=gas_price * gas_limit,
                    denom=self.network.fee_denom,
                )
            ]

            tx = (
                tx.with_gas(gas_limit)
                .with_fee(fee)
                .with_memo("")
                .with_timeout_height(self.client.timeout_height)
            )
            sign_doc = tx.get_sign_doc(self.pub_key)
            sig = self.priv_key.sign(sign_doc.SerializeToString())
            tx_raw_bytes = tx.get_tx_data(sig, self.pub_key)

            res = await self.client.broadcast_tx_sync_mode(tx_raw_bytes)
            # standardized return arguments
            return {
                "success": True,
                "result": res,
                "gas_wanted": gas_limit,
                "gas_fee": f"{gas_fee} INJ",
            }
        except Exception as e:
            return {"success": False, "error": detailed_exception_info(e)}
