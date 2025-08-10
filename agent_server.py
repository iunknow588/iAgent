from openai import OpenAI
import os
from dotenv import load_dotenv
from quart import Quart, request, jsonify
from datetime import datetime
import argparse
from injective_functions.factory import InjectiveClientFactory
from injective_functions.utils.function_helper import (
    FunctionSchemaLoader,
    FunctionExecutor,
)
import json
import asyncio
import logging
from hypercorn.config import Config
from hypercorn.asyncio import serve
import aiohttp
import asyncio as _asyncio_for_shutdown
from network.connectivity import check_injective_connectivity, ConnectivityRegistry

# Set up logging
logger = logging.getLogger(__name__)

# Initialize Quart app (async version of Flask)
app = Quart(__name__)


class InjectiveChatAgent:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Get API configuration from environment variables
        self.selected_model = os.getenv("SELECTED_MODEL", "auto").lower()  # auto, deepseek, openai, or chatanywhere
        
        # Initialize API configurations
        self.api_configs = {}
        
        # DeepSeek API configuration
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        if deepseek_key:
            self.api_configs["deepseek"] = {
                "api_key": deepseek_key,
                "base_url": os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com"),
                "model": "deepseek-chat"
            }
        
        # OpenAI API configuration
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.api_configs["openai"] = {
                "api_key": openai_key,
                "base_url": os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com"),
                "model": "gpt-4o"
            }
        
        # ChatAnywhere API configuration (if using chatanywhere)
        if "api.chatanywhere.tech" in os.getenv("OPENAI_API_BASE_URL", ""):
            self.api_configs["chatanywhere"] = {
                "api_key": openai_key,
                "base_url": os.getenv("OPENAI_API_BASE_URL", "https://api.chatanywhere.tech"),
                "model": "gpt-4o"
            }
        
        # Select API based on user preference
        self.selected_api = self._select_api()
        
        if not self.selected_api:
            raise ValueError(
                "No API configuration found. Please set either DEEPSEEK_API_KEY or OPENAI_API_KEY environment variable."
            )
        
        # Initialize OpenAI client with selected API configuration
        self.client = OpenAI(
            api_key=self.selected_api["api_key"], 
            base_url=self.selected_api["base_url"]
        )
        
        print(f"✅ 使用 {self.selected_api['type']} API")

        # Initialize conversation histories
        self.conversations = {}
        # Initialize injective agents
        self.agents = {}
        base_dir = os.path.dirname(os.path.abspath(__file__))
        schema_paths = [
            os.path.join(base_dir, "injective_functions/account/account_schema.json"),
            os.path.join(base_dir, "injective_functions/auction/auction_schema.json"),
            os.path.join(base_dir, "injective_functions/authz/authz_schema.json"),
            os.path.join(base_dir, "injective_functions/bank/bank_schema.json"),
            os.path.join(base_dir, "injective_functions/exchange/exchange_schema.json"),
            os.path.join(base_dir, "injective_functions/staking/staking_schema.json"),
            os.path.join(base_dir, "injective_functions/token_factory/token_factory_schema.json"),
            os.path.join(base_dir, "injective_functions/utils/utils_schema.json"),
        ]
        self.function_schemas = FunctionSchemaLoader.load_schemas(schema_paths)
        
        # Convert schemas for tools format if needed
        self._tools = []
        try:
            fn_list = self.function_schemas.get("functions", []) if isinstance(self.function_schemas, dict) else []
            self._tools = [
                {"type": "function", "function": fn}
                for fn in fn_list
                if isinstance(fn, dict) and fn.get("name") and fn.get("parameters")
            ]
        except Exception:
            self._tools = []
    
    def _select_api(self):
        """Select API based on user preference"""
        # If user specified a specific model
        if self.selected_model in self.api_configs:
            self.api_configs[self.selected_model]["type"] = self.selected_model
            return self.api_configs[self.selected_model]
        
        # If auto mode, show available options and let user choose
        if self.selected_model == "auto":
            print("🤖 检测到多个可用的API配置:")
            available_apis = list(self.api_configs.keys())
            
            if len(available_apis) == 1:
                # Only one API available, use it
                api_type = available_apis[0]
                self.api_configs[api_type]["type"] = api_type
                return self.api_configs[api_type]
            elif len(available_apis) > 1:
                print("📋 可用的API类型:")
                for i, api_type in enumerate(available_apis, 1):
                    print(f"   {i}. {api_type.upper()}")
                
                print(f"\n💡 请设置 SELECTED_MODEL 环境变量来选择API:")
                print(f"   例如: SELECTED_MODEL=deepseek")
                print(f"   或者: SELECTED_MODEL=openai")
                print(f"   或者: SELECTED_MODEL=chatanywhere")
                
                # Use the first available API as default
                api_type = available_apis[0]
                print(f"⚠️  使用默认API: {api_type}")
                self.api_configs[api_type]["type"] = api_type
                return self.api_configs[api_type]
        
        # If specified model is not available
        if self.selected_model != "auto":
            available_apis = list(self.api_configs.keys())
            print(f"❌ 指定的模型 '{self.selected_model}' 不可用")
            print(f"📋 可用的API类型: {', '.join(available_apis)}")
            print(f"💡 请设置正确的 SELECTED_MODEL 环境变量")
            
            if available_apis:
                # Use the first available API as fallback
                api_type = available_apis[0]
                print(f"⚠️  使用备用API: {api_type}")
                self.api_configs[api_type]["type"] = api_type
                return self.api_configs[api_type]
        
        return None

    async def initialize_agent(
        self, agent_id: str, private_key: str, environment: str = "testnet"
    ) -> None:
        """Initialize Injective clients if they don't exist"""
        if agent_id not in self.agents:
            # Skip initialization if private_key is invalid or default
            if private_key and private_key != "default" and len(private_key) >= 64:
                try:
                    clients = await InjectiveClientFactory.create_all(
                        private_key=private_key, network_type=environment
                    )
                    self.agents[agent_id] = clients
                except Exception as e:
                    print(f"Failed to initialize agent with private key: {str(e)}")
                    # Continue without Injective clients for general chat
            else:
                print(f"Skipping Injective client initialization for agent {agent_id} - no valid private key provided")

    async def execute_function(
        self, function_name: str, arguments: dict, agent_id: str
    ) -> dict:
        """Execute the appropriate Injective function with error handling"""
        try:
            # Get the client dictionary for this agent
            clients = self.agents.get(agent_id)
            if not clients:
                return {
                    "error": "Injective functions require valid credentials. Please provide a valid private key to use blockchain functions.",
                    "success": False,
                    "details": {"function": function_name, "arguments": arguments},
                }

            return await FunctionExecutor.execute_function(
                clients=clients, function_name=function_name, arguments=arguments
            )

        except Exception as e:
            return {
                "error": str(e),
                "success": False,
                "details": {"function": function_name, "arguments": arguments},
            }

    async def get_response(
        self,
        message,
        session_id="default",
        private_key=None,
        agent_id=None,
        environment="testnet",
    ):
        """Get response from API."""
        await self.initialize_agent(
            agent_id=agent_id, private_key=private_key, environment=environment
        )
        print("initialized agents")
        try:
            # Initialize conversation history for new sessions
            if session_id not in self.conversations:
                self.conversations[session_id] = []

            # Add user message to conversation history
            self.conversations[session_id].append({"role": "user", "content": message})

            # Use the selected API's model
            model = self.selected_api["model"]

            # Get response from API
            # Build function/tool calling params depending on provider
            provider_type = self.selected_api["type"]
            messages = [
                    {
                        "role": "system",
                        "content": """You are an AI assistant for Injective Chain. Help with blockchain questions and functions. 

IMPORTANT INSTRUCTIONS:
1. When users ask to "check balance", "get balance", "show balance", or similar balance-related queries, ALWAYS call the query_balances function to get real balance data.
2. When users ask to "check orders", "get orders", "show orders", call the appropriate order-related functions.
3. When users ask to "show markets", "get markets", "view markets", call the appropriate market-related functions.
4. When users ask to "check positions", "get positions", "view positions", call the appropriate position-related functions.
5. When users ask to "check history", "get history", "view history", call the appropriate history-related functions.

Available functions:
- query_balances: Query token balances for the current address
- query_spendable_balances: Query spendable token balances
- get_subaccount_orders: Get orders for the current subaccount
- get_derivatives_orderbook: Get derivatives orderbook
- get_spot_orderbook: Get spot orderbook
- trader_derivative_orders: Get derivative orders
- trader_spot_orders: Get spot orders

Use 'BTC/USDT PERP' for Bitcoin perpetual and 'ETH/USDT PERP' for Ethereum perpetual. Confirm before executing actions.

When users ask for balance information, immediately call query_balances function without asking for additional details unless specifically needed."""
                    }
                ] + self.conversations[session_id]

            create_kwargs = {
                "model": model,
                "messages": messages,
                "max_tokens": 2000,
                "temperature": 0.7,
            }
            if provider_type == "deepseek":
                if self._tools:
                    create_kwargs.update({"tools": self._tools, "tool_choice": "auto"})
            else:
                # default to legacy functions if available
                fn_list = self.function_schemas.get("functions", []) if isinstance(self.function_schemas, dict) else []
                if fn_list:
                    create_kwargs.update({"functions": fn_list, "function_call": "auto"})

            response = await asyncio.to_thread(self.client.chat.completions.create, **create_kwargs)

            response_message = response.choices[0].message
            print(response_message)

            # 如果模型未触发函数调用，但用户请求了余额/相关信息，则执行回退函数调用
            try:
                user_intent = str(message).lower().strip()
                assistant_text = (response_message.content or "").lower() if hasattr(response_message, "content") else ""
                balance_triggers = [
                    "check balance",
                    "get balance",
                    "show balance",
                    "view balance",
                    "balance",
                ]
                should_fallback_balance = (
                    any(t in user_intent for t in balance_triggers)
                    or ("balance" in user_intent)
                    or ("query_balances" in assistant_text)
                    or ("calling function" in assistant_text and "balance" in assistant_text)
                )
                    
                # Also check for subaccount balance requests
                subaccount_triggers = [
                    "subaccount",
                    "deposits", 
                    "trading balance",
                    "exchange balance"
                ]
                should_fallback_subaccount = any(t in user_intent for t in subaccount_triggers)
            except Exception:
                should_fallback_balance = False
                should_fallback_subaccount = False

            # Handle function calling (native or fallback)
            if (
                hasattr(response_message, "function_call")
                and response_message.function_call
            ) or should_fallback_balance or should_fallback_subaccount:
                # Extract function details
                if hasattr(response_message, "function_call") and response_message.function_call:
                    function_name = response_message.function_call.name
                    function_args = json.loads(response_message.function_call.arguments)
                else:
                    # Fallback based on intent
                    if should_fallback_subaccount:
                        function_name = "get_subaccount_deposits"
                        function_args = {"subaccount_idx": 0}
                    else:
                        # Fallback to query_balances when intent indicates a balance request
                        function_name = "query_balances"
                        function_args = {}
                # Execute the function
                function_response = await self.execute_function(
                    function_name, function_args, agent_id
                )

                # Add function call and response to conversation
                tool_call_id = f"call_{function_name}"
                self.conversations[session_id].append(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tool_call_id,
                                "type": "function",
                                "function": {
                                    "name": function_name,
                                    "arguments": json.dumps(function_args),
                                },
                            }
                        ],
                    }
                )

                self.conversations[session_id].append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": function_name,
                        "content": json.dumps(function_response),
                    }
                )

                # Get final response with appropriate model
                final_model = self.selected_api["model"]

                second_kwargs = {
                    "model": final_model,
                    "messages": self.conversations[session_id],
                    "max_tokens": 2000,
                    "temperature": 0.7,
                }
                # include tools again if provider uses tools (not strictly required for the second round)
                if provider_type == "deepseek" and self._tools:
                    second_kwargs.update({"tools": self._tools, "tool_choice": "none"})
                second_response = await asyncio.to_thread(self.client.chat.completions.create, **second_kwargs)

                final_response = second_response.choices[0].message.content.strip()
                self.conversations[session_id].append(
                    {"role": "assistant", "content": final_response}
                )

                return {
                    "response": final_response,
                    "function_call": {
                        "name": function_name,
                        "result": function_response,
                    },
                    "session_id": session_id,
                }

            # Handle regular response
            bot_message = response_message.content
            if bot_message:
                self.conversations[session_id].append(
                    {"role": "assistant", "content": bot_message}
                )

                return {
                    "response": bot_message,
                    "function_call": None,
                    "session_id": session_id,
                }
            else:
                default_response = "I'm here to help you with trading on Injective Chain. You can ask me about trading, checking balances, making transfers, or staking. How can I assist you today?"
                self.conversations[session_id].append(
                    {"role": "assistant", "content": default_response}
                )

                return {
                    "response": default_response,
                    "function_call": None,
                    "session_id": session_id,
                }

        except Exception as e:
            error_response = f"I apologize, but I encountered an error: {str(e)}. How else can I help you?"
            return {
                "response": error_response,
                "function_call": None,
                "session_id": session_id,
            }

    def clear_history(self, session_id="default"):
        """Clear conversation history for a specific session."""
        if session_id in self.conversations:
            self.conversations[session_id].clear()

    def get_history(self, session_id="default"):
        """Get conversation history for a specific session."""
        return self.conversations.get(session_id, [])


# Initialize chat agent
agent = InjectiveChatAgent()


@app.route("/", methods=["GET"])
async def root():
    """Root endpoint with API information"""
    return jsonify({
        "message": "Welcome to Injective Agent API",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "This endpoint - API information",
            "GET /ping": "Health check",
            "POST /chat": "Chat with the agent",
            "GET /history": "Get chat history",
            "POST /clear": "Clear chat history"
        },
        "status": "running"
    })


@app.route("/ping", methods=["GET"])
async def ping():
    """Health check endpoint"""
    return jsonify(
        {"status": "ok", "timestamp": datetime.now().isoformat(), "version": "1.0.0"}
    )


@app.route("/network/connectivity", methods=["GET"])
async def connectivity_endpoint():
    """Check Injective endpoints connectivity and return cached + fresh results."""
    try:
        env = request.args.get("environment", "testnet")
        registry = ConnectivityRegistry.instance()
        
        # 获取缓存结果
        cached = {k: v.to_dict() for k, v in registry.get_results(env).items()}
        
        # 获取缓存信息
        cache_info = registry.get_cache_info(env)
        
        # 检查是否需要重新测试
        should_recheck = registry.should_recheck(env)
        
        # 如果需要重新测试或没有缓存，运行新的检测
        if should_recheck or not cached:
            logger.info(f"Running fresh connectivity check for {env}")
            results = await check_injective_connectivity(env, timeout=5.0)
            fresh = {k: v.to_dict() for k, v in results.items()}
        else:
            logger.info(f"Using cached results for {env}")
            fresh = cached
        
        return jsonify({
            "environment": env, 
            "cached": cached, 
            "fresh": fresh,
            "cache_info": cache_info,
            "should_recheck": should_recheck
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/network/status", methods=["GET"])
async def network_status_endpoint():
    """Get detailed network status including cache information and endpoint availability."""
    try:
        env = request.args.get("environment", "testnet")
        registry = ConnectivityRegistry.instance()
        
        # 获取缓存信息
        cache_info = registry.get_cache_info(env)
        
        # 获取当前最佳端点
        from network.connectivity import get_best_endpoints
        best_endpoints = get_best_endpoints(env)
        
        # 获取端点状态摘要
        from network.connectivity import get_endpoint_status_summary
        status_summary = get_endpoint_status_summary(env)
        
        return jsonify({
            "environment": env,
            "cache_info": cache_info,
            "best_endpoints": best_endpoints,
            "status_summary": status_summary,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/network/refresh", methods=["POST"])
async def network_refresh_endpoint():
    """Force refresh network connectivity for specified environment."""
    try:
        data = await request.get_json() or {}
        env = data.get("environment", "testnet")
        
        logger.info(f"Force refreshing network connectivity for {env}")
        
        # 强制刷新
        from network.connectivity import refresh_endpoints
        new_endpoints = refresh_endpoints(env)
        
        # 获取新的状态
        registry = ConnectivityRegistry.instance()
        cache_info = registry.get_cache_info(env)
        
        return jsonify({
            "environment": env,
            "refreshed_endpoints": new_endpoints,
            "cache_info": cache_info,
            "message": f"Network connectivity refreshed for {env}",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/chat", methods=["POST"])
async def chat_endpoint():
    """Main chat endpoint"""
    try:
        data = await request.get_json()
        
        # 检查请求数据是否为空
        if not data:
            return (
                jsonify(
                    {
                        "error": "No data provided",
                        "response": "Please provide a valid JSON request with a message.",
                        "session_id": "default",
                        "agent_id": "default",
                        "agent_key": "default",
                        "environment": "testnet",
                    }
                ),
                400,
            )
        
        # 检查消息字段
        if "message" not in data or not data["message"] or data["message"].strip() == "":
            return (
                jsonify(
                    {
                        "error": "No message provided",
                        "response": "Please provide a message to continue our conversation.",
                        "session_id": data.get("session_id", "default"),
                        "agent_id": data.get("agent_id", "default"),
                        "agent_key": data.get("agent_key", "default"),
                        "environment": data.get("environment", "testnet"),
                    }
                ),
                400,
            )

        session_id = data.get("session_id", "default")
        private_key = data.get("agent_key", "default")
        agent_id = data.get("agent_id", "default")
        environment = data.get("environment", "testnet")
        
        # 验证环境参数
        if environment not in ["testnet", "mainnet"]:
            environment = "testnet"
        
        # 检查是否为直接函数调用
        if "function_name" in data and "function_args" in data:
            # 直接函数调用模式
            function_name = data["function_name"]
            function_args = data["function_args"]
            
            # 初始化代理
            await agent.initialize_agent(agent_id, private_key, environment)
            
            # 直接执行函数
            function_response = await agent.execute_function(function_name, function_args, agent_id)
            
            # 构建响应
            response = {
                "response": f"Function {function_name} executed successfully",
                "function_call": {
                    "name": function_name,
                    "result": function_response,
                },
                "session_id": session_id,
            }
        else:
            # 常规聊天模式
            response = await agent.get_response(
                data["message"], session_id, private_key, agent_id, environment
            )

        return jsonify(response)
    except json.JSONDecodeError:
        return (
            jsonify(
                {
                    "error": "Invalid JSON format",
                    "response": "Please provide a valid JSON request.",
                    "session_id": "default",
                }
            ),
            400,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "error": str(e),
                    "response": "I apologize, but I encountered an error. Please try again.",
                    "session_id": data.get("session_id", "default") if 'data' in locals() else "default",
                }
            ),
            500,
        )


@app.route("/history", methods=["GET"])
async def history_endpoint():
    """Get chat history endpoint"""
    session_id = request.args.get("session_id", "default")
    return jsonify({"history": agent.get_history(session_id)})


@app.route("/clear", methods=["POST"])
async def clear_endpoint():
    """Clear chat history endpoint"""
    session_id = request.args.get("session_id", "default")
    agent.clear_history(session_id)
    return jsonify({"status": "success"})


@app.route("/shutdown", methods=["POST"])
async def shutdown_endpoint():
    """Shutdown the API server gracefully.

    Optional auth: set env SERVER_SHUTDOWN_TOKEN and provide {"token": "..."} in the request body.
    """
    try:
        data = await request.get_json() or {}
        env_token = os.getenv("SERVER_SHUTDOWN_TOKEN")
        if env_token and data.get("token") != env_token:
            return jsonify({"error": "Unauthorized"}), 403

        async def _delayed_exit():
            # Give time for the HTTP response to be sent
            await _asyncio_for_shutdown.sleep(0.5)
            os._exit(0)

        _asyncio_for_shutdown.create_task(_delayed_exit())
        return jsonify({"status": "shutting_down"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def main():
    parser = argparse.ArgumentParser(description="Run the chatbot API server")
    parser.add_argument("--port", type=int, default=5000, help="Port for API server")
    parser.add_argument("--host", default="0.0.0.0", help="Host for API server")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument("--skip-network-check", action="store_true", help="Skip network connectivity check on startup")
    args = parser.parse_args()

    # 启动时进行网络连接性检查
    if not args.skip_network_check:
        print("🔍 检查网络连接性...")
        try:
            # 检查testnet和mainnet的连接性
            async def check_networks():
                results = {}
                for env in ["testnet", "mainnet"]:
                    print(f"  检查 {env} 网络端点...")
                    env_results = await check_injective_connectivity(env, timeout=5.0)
                    results[env] = env_results
                    
                    # 显示结果
                    reachable_count = sum(1 for status in env_results.values() if status.reachable)
                    total_count = len(env_results)
                    print(f"    {env}: {reachable_count}/{total_count} 端点可达")
                    
                    for name, status in env_results.items():
                        status_icon = "✅" if status.reachable else "❌"
                        latency = f"{status.latency_ms:.1f}ms" if status.latency_ms else "N/A"
                        print(f"      {status_icon} {name:12s} {latency:>8s}  {status.target}")
                        if status.error:
                            print(f"        错误: {status.error}")
                
                return results
            
            # 运行网络检查
            network_results = asyncio.run(check_networks())
            print("✅ 网络连接性检查完成")
            
        except Exception as e:
            print(f"⚠️  网络连接性检查失败: {e}")
            print("   服务器将继续启动，但某些功能可能受影响")
    else:
        print("⚠️  跳过网络连接性检查")

    config = Config()
    config.bind = [f"{args.host}:{args.port}"]
    config.debug = args.debug

    print(f"Starting API server on {args.host}:{args.port}")
    asyncio.run(serve(app, config))


if __name__ == "__main__":
    main()
