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
from hypercorn.config import Config
from hypercorn.asyncio import serve
import aiohttp

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
        schema_paths = [
            "./injective_functions/account/account_schema.json",
            "./injective_functions/auction/auction_schema.json",
            "./injective_functions/authz/authz_schema.json",
            "./injective_functions/bank/bank_schema.json",
            "./injective_functions/exchange/exchange_schema.json",
            "./injective_functions/staking/staking_schema.json",
            "./injective_functions/token_factory/token_factory_schema.json",
            "./injective_functions/utils/utils_schema.json",
        ]
        self.function_schemas = FunctionSchemaLoader.load_schemas(schema_paths)
    
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
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model,
                messages=[
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
                ]
                + self.conversations[session_id],
                functions=self.function_schemas,
                function_call="auto",
                max_tokens=2000,
                temperature=0.7,
            )

            response_message = response.choices[0].message
            print(response_message)
            # Handle function calling
            if (
                hasattr(response_message, "function_call")
                and response_message.function_call
            ):
                # Extract function details
                function_name = response_message.function_call.name
                function_args = json.loads(response_message.function_call.arguments)
                # Execute the function
                function_response = await self.execute_function(
                    function_name, function_args, agent_id
                )

                # Add function call and response to conversation
                self.conversations[session_id].append(
                    {
                        "role": "assistant",
                        "content": None,
                        "function_call": {
                            "name": function_name,
                            "arguments": json.dumps(function_args),
                        },
                    }
                )

                self.conversations[session_id].append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": json.dumps(function_response),
                    }
                )

                # Get final response with appropriate model
                final_model = self.selected_api["model"]

                second_response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=final_model,
                    messages=self.conversations[session_id],
                    max_tokens=2000,
                    temperature=0.7,
                )

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


def main():
    parser = argparse.ArgumentParser(description="Run the chatbot API server")
    parser.add_argument("--port", type=int, default=5000, help="Port for API server")
    parser.add_argument("--host", default="0.0.0.0", help="Host for API server")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()

    config = Config()
    config.bind = [f"{args.host}:{args.port}"]
    config.debug = args.debug

    print(f"Starting API server on {args.host}:{args.port}")
    asyncio.run(serve(app, config))


if __name__ == "__main__":
    main()
