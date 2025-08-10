#!/usr/bin/env python3
"""
CLI客户端界面 - Injective Agent API
💬 交互式命令行客户端，用于与运行中的服务器进行通信
功能：代理管理、聊天交互、命令处理、响应格式化

原文件名：quickstart.py
新文件名：quick_start_client.py
"""

import os
import sys
import time
import threading
from datetime import datetime
import colorama
from colorama import Fore, Style, Back
import requests
import argparse
import json
from decimal import Decimal
from typing import Dict, Optional
from pyinjective.core.network import Network
from app.agent_manager import AgentManager


# Initialize colorama for cross-platform colored output
colorama.init()


class InjectiveCLI:
    """Enhanced CLI interface with agent management"""

    def __init__(self, api_url: str, debug: bool = False):
        self.api_url = api_url
        self.debug = debug
        self.session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.animation_stop = False
        self.animation_thread = None  # 初始化 animation_thread 属性
        self.agent_manager = AgentManager()
        
        # 会话管理
        self.session_start_time = datetime.now()
        self.command_history = []

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system("cls" if os.name == "nt" else "clear")

    def start_animation(self):
        """Start the animation in a new thread"""
        self.animation_stop = False
        # 确保之前的线程已经停止
        if self.animation_thread and self.animation_thread.is_alive():
            self.stop_animation()
        self.animation_thread = threading.Thread(target=self.display_typing_animation)
        self.animation_thread.daemon = True
        self.animation_thread.start()

    def stop_animation(self):
        """Stop the animation and clean up"""
        if self.animation_thread and self.animation_thread.is_alive():
            self.animation_stop = True
            self.animation_thread.join(timeout=1.0)  # Wait for animation to finish
            self.animation_thread = None

    def display_typing_animation(self):
        """Display a typing animation while waiting for response."""
        animation = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while not self.animation_stop:
            sys.stdout.write(
                f"\r{Fore.YELLOW}Processing transaction {animation[i]}{Style.RESET_ALL}"
            )
            sys.stdout.flush()
            time.sleep(0.1)
            i = (i + 1) % len(animation)
        # Clear the animation line when done
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()

    def _format_network_details(self) -> str:
        """返回包含实际链信息的网络字符串"""
        try:
            current_net = self.agent_manager.get_current_network()
            inj_net = Network.testnet() if current_net == "testnet" else Network.mainnet()
            return f"{current_net.upper()} (chain_id: {inj_net.chain_id}, fee_denom: {inj_net.fee_denom})"
        except Exception:
            return self.agent_manager.get_current_network().upper()

    def list_agents_by_network(self, agents, environment):
        if not agents and self.agent_manager.current_network == environment:
            print(
                f"{Fore.YELLOW}No agents configured for {self.agent_manager.get_current_network().upper()}{Style.RESET_ALL}"
            )
            return False
        else:
            print(
                f"{Fore.CYAN}Available Agents on {self.agent_manager.get_current_network().upper()}:{Style.RESET_ALL}"
            )
            for name, info in agents.items():
                current = "*" if name == self.agent_manager.current_agent else " "
                print(f"{current} {name}: {info['address']}")
            return True

    def format_response(self, response_text, response_type=None):
        """Format and clean up the response text based on type."""
        if not response_text:
            return "No response"

        try:
            # Try to parse as JSON first
            response_data = (
                json.loads(response_text)
                if isinstance(response_text, str)
                else response_text
            )

            # Determine the type of response based on content
            if isinstance(response_data, dict):
                if "balances" in response_data:
                    return self.format_balance_response(response_data)
                elif any(
                    key in response_data for key in ["result", "gas_wanted", "gas_fee"]
                ):
                    return self.format_transaction_response(response_data)
        except:
            pass

        # Default formatting for regular messages
        return response_text

    def format_transaction_response(self, response):
        """Format blockchain transaction response."""
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except:
                return response

        if isinstance(response, dict):
            if "error" in response:
                return (
                    f"{Fore.RED}Transaction Error: {response['error']}{Style.RESET_ALL}"
                )

            result = []
            if "result" in response:
                tx_result = response["result"]
                result.append(f"{Fore.GREEN}Transaction Successful{Style.RESET_ALL}")
                if isinstance(tx_result, dict):
                    if "txhash" in tx_result:
                        result.append(f"Transaction Hash: {tx_result['txhash']}")
                    if "height" in tx_result:
                        result.append(f"Block Height: {tx_result['height']}")

            if "gas_wanted" in response:
                result.append(f"Gas Wanted: {response['gas_wanted']}")
            if "gas_fee" in response:
                result.append(f"Gas Fee: {response['gas_fee']}")

            return "\n".join(result)

        return str(response)

    def format_balance_response(self, response):
        """Format balance query response."""
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except:
                return response

        if isinstance(response, dict):
            if "error" in response:
                return f"{Fore.RED}Query Error: {response['error']}{Style.RESET_ALL}"

            if "balances" in response:
                result = [f"{Fore.CYAN}Account Balances:{Style.RESET_ALL}"]
                for token in response["balances"]:
                    amount = Decimal(token.get("amount", 0)) / Decimal(
                        10**18
                    )  # Convert from wei
                    denom = token.get("denom", "UNKNOWN")
                    result.append(f"- {amount:.8f} {denom}")
                return "\n".join(result)

        return str(response)

    def display_response(self, response_text, debug_info=None):
        """Display the bot's response with proper formatting."""
        sys.stdout.write("\r" + " " * 50 + "\r")

        if debug_info:
            print(
                f"{Fore.YELLOW}Debug: {json.dumps(debug_info, indent=2)}{Style.RESET_ALL}"
            )

        formatted_response = self.format_response(response_text)
        print(f"{Fore.BLUE}Response: {formatted_response}{Style.RESET_ALL}")
        print()

    def display_banner(self):
        """Display welcome banner with agent information"""
        self.clear_screen()
        print(f"{Fore.CYAN}=" * 80)
        print(
            Fore.BLUE
            + """
        ██╗███╗   ██╗     ██╗███████╗ ██████╗████████╗██╗██╗   ██╗███████╗
        ██║████╗  ██║     ██║██╔════╝██╔════╝╚══██╔══╝██║██║   ██║██╔════╝
        ██║██╔██╗ ██║     ██║█████╗  ██║        ██║   ██║██║   ██║█████╗  
        ██║██║╚██╗██║██   ██║██╔══╝  ██║        ██║   ██║╚██╗ ██╔╝██╔══╝  
        ██║██║ ╚████║╚█████╔╝███████╗╚██████╗   ██║   ██║ ╚████╔╝ ███████╗
        ╚═╝╚═╝  ╚═══╝ ╚════╝ ╚══════╝ ╚═════╝   ╚═╝   ╚═╝  ╚═══╝  ╚══════╝
        """
            + Fore.RESET
        )
        print(
            f"{Back.BLUE}{Fore.WHITE} Injective Chain Interactive Agent CLI Client {Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}Connected to: {self.api_url}")
        print(f"Session ID: {self.session_id}")
        print(f"Current Network: {self._format_network_details()}")

        current_agent = self.agent_manager.get_current_agent()
        if current_agent:
            print(f"Current Agent: {self.agent_manager.current_agent}")
            print(f"Agent Address: {current_agent['address']}")
        else:
            print(
                f"{Fore.YELLOW}No agent selected. Please select an agent{Style.RESET_ALL}"
            )

        print(f"{Fore.CYAN}=" * 80)
        print(f"{Fore.YELLOW}Available Commands:")
        print("General: quit, clear, help, history, ping, debug, session")
        print("Network: switch_network [mainnet|testnet]")
        print("Agents: create_agent, delete_agent, switch_agent, list_agents")
        print("Blockchain: check balance, get orders, show markets, view positions")
        print("Server: shutdown_server [token]")
        print("=" * 80 + Style.RESET_ALL)

    def handle_agent_commands(self, command: str, args: str) -> bool:
        """Handle agent-related commands"""
        try:
            if command == "help":
                self.display_banner()
                return True
                
            elif command == "ping":
                # 实现ping命令
                try:
                    url = f"{self.api_url.rstrip('/')}/ping"
                    headers = {"Content-Type": "application/json", "Accept": "application/json"}
                    
                    print(f"{Fore.YELLOW}Pinging server at {url}...{Style.RESET_ALL}")
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"{Fore.GREEN}✅ Server is online!{Style.RESET_ALL}")
                        print(f"   Status: {data.get('status', 'unknown')}")
                        print(f"   Version: {data.get('version', 'unknown')}")
                        print(f"   Timestamp: {data.get('timestamp', 'unknown')}")
                    else:
                        print(f"{Fore.RED}❌ Server responded with status code: {response.status_code}{Style.RESET_ALL}")
                        
                except requests.exceptions.Timeout:
                    print(f"{Fore.RED}❌ Request timed out. Server may be offline or slow.{Style.RESET_ALL}")
                except requests.exceptions.ConnectionError:
                    print(f"{Fore.RED}❌ Connection failed. Server may be offline.{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}❌ Ping failed: {str(e)}{Style.RESET_ALL}")
                return True
                
            elif command == "switch_network":
                if not args or args.lower() not in ["mainnet", "testnet"]:
                    print(
                        f"{Fore.RED}Error: Please specify 'mainnet' or 'testnet'{Style.RESET_ALL}"
                    )
                    return True

                # Clear current agent when switching networks
                self.agent_manager.current_agent = None
                self.agent_manager.switch_network(args.lower())
                print(f"{Fore.GREEN}Switched to {args.upper()}{Style.RESET_ALL}")
                self.display_banner()
                return True

            elif command == "create_agent":
                if not args:
                    print(f"{Fore.RED}Error: Agent name required{Style.RESET_ALL}")
                    return True
                agent_info = self.agent_manager.create_agent(args)
                print(
                    f"{Fore.GREEN}Created agent '{args}' on {self.agent_manager.get_current_network().upper()}{Style.RESET_ALL}"
                )
                print(f"Address: {agent_info['address']}")
                return True

            elif command == "delete_agent":
                if not args:
                    print(f"{Fore.RED}Error: Agent name required{Style.RESET_ALL}")
                    return True
                self.agent_manager.delete_agent(args)
                print(f"{Fore.GREEN}Deleted agent '{args}'{Style.RESET_ALL}")
                return True

            elif command == "switch_agent":
                if not args:
                    print(f"{Fore.RED}Error: Agent name required{Style.RESET_ALL}")
                    return True
                self.agent_manager.switch_agent(args)
                print(
                    f"{Fore.GREEN}Switched to agent '{args}' on {self.agent_manager.get_current_network().upper()}{Style.RESET_ALL}"
                )
                return True

            elif command == "list_agents":
                # agents = self.agent_manager.list_agents()
                (
                    mainnet_agents,
                    testnet_agents,
                ) = self.agent_manager.get_agent_based_on_network()
                if self.agent_manager.current_network == "mainnet":
                    self.list_agents_by_network(mainnet_agents, "mainnet")
                else:
                    self.list_agents_by_network(testnet_agents, "testnet")
                return True
                
            elif command == "session":
                # 显示当前会话信息
                print(f"{Fore.CYAN}📋 当前会话信息{Style.RESET_ALL}")
                print(f"   会话ID: {self.session_id}")
                print(f"   服务器地址: {self.api_url}")
                print(f"   调试模式: {'开启' if self.debug else '关闭'}")
                
                # 显示当前网络信息
                current_network = self.agent_manager.get_current_network()
                print(f"   当前网络: {current_network.upper()}")
                
                # 显示当前代理信息
                current_agent = self.agent_manager.get_current_agent()
                if current_agent:
                    print(f"   当前代理: {current_agent.get('name', 'unknown')}")
                    print(f"   代理地址: {current_agent.get('address', 'unknown')}")
                    print(f"   创建时间: {current_agent.get('created_at', 'unknown')}")
                else:
                    print(f"   当前代理: {Fore.YELLOW}未选择{Style.RESET_ALL}")
                
                # 显示会话统计信息
                print(f"\n{Fore.CYAN}📊 会话统计{Style.RESET_ALL}")
                print(f"   会话开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   运行时长: {self._get_session_duration()}")
                
                return True
                
            elif command == "debug":
                # 切换调试模式
                self.debug = not self.debug
                status = "开启" if self.debug else "关闭"
                print(f"{Fore.GREEN}✅ 调试模式已{status}{Style.RESET_ALL}")
                return True
                
            elif command == "history":
                # 显示命令历史
                print(f"{Fore.CYAN}📜 命令历史{Style.RESET_ALL}")
                if hasattr(self, 'command_history') and self.command_history:
                    for i, cmd in enumerate(self.command_history[-10:], 1):  # 显示最近10条
                        print(f"   {i:2d}. {cmd}")
                else:
                    print(f"   {Fore.YELLOW}暂无命令历史{Style.RESET_ALL}")
                return True

            elif command == "shutdown_server":
                try:
                    url = f"{self.api_url.rstrip('/')}/shutdown"
                    headers = {"Content-Type": "application/json", "Accept": "application/json"}
                    payload = {}
                    if args:
                        payload["token"] = args.strip()
                    print(f"{Fore.YELLOW}Requesting server shutdown...{Style.RESET_ALL}")
                    resp = requests.post(url, json=payload, headers=headers, timeout=5)
                    if resp.status_code == 200:
                        print(f"{Fore.GREEN}✅ Server acknowledged shutdown.{Style.RESET_ALL}")
                    elif resp.status_code == 403:
                        print(f"{Fore.RED}❌ Unauthorized. Invalid or missing shutdown token.{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}❌ Shutdown failed: HTTP {resp.status_code} - {resp.text}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}❌ Shutdown request error: {str(e)}{Style.RESET_ALL}")
                return True

            elif command == "netcheck":
                try:
                    url = f"{self.api_url.rstrip('/')}/network/connectivity"
                    params = {"environment": self.agent_manager.get_current_network()}
                    headers = {"Accept": "application/json"}
                    print(f"{Fore.YELLOW}Checking Injective endpoint connectivity...{Style.RESET_ALL}")
                    resp = requests.get(url, params=params, headers=headers, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json()
                        fresh = data.get("fresh", {})
                        print(f"{Fore.GREEN}✅ Connectivity results ({data.get('environment','')}){Style.RESET_ALL}")
                        for name, item in fresh.items():
                            ok = 'OK' if item.get('reachable') else 'FAIL'
                            lat = item.get('latency_ms')
                            target = item.get('target')
                            print(f"  - {name:14s} {ok:4s}  {lat:>6} ms  {target}")
                    else:
                        print(f"{Fore.RED}❌ Netcheck failed: HTTP {resp.status_code} - {resp.text}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}❌ Netcheck error: {str(e)}{Style.RESET_ALL}")
                return True
                
            # 处理复合命令（如 "check balance", "get balance" 等）
            elif command in ["check", "get", "show", "view"]:
                return self._handle_composite_command(command, args)
                
            else:
                # 检查是否是拼写错误
                known_commands = ["help", "ping", "switch_network", "create_agent", "delete_agent", "switch_agent", "list_agents", "session", "debug", "history", "check", "get", "show", "view"]
                suggestions = []
                
                for known_cmd in known_commands:
                    if self._similarity(command, known_cmd) > 0.6:  # 相似度阈值
                        suggestions.append(known_cmd)
                
                if suggestions:
                    print(f"{Fore.YELLOW}❓ 未知命令: '{command}'{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}💡 您可能想要输入: {', '.join(suggestions)}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}💡 输入 'help' 查看所有可用命令{Style.RESET_ALL}")
                else:
                    print(f"{Fore.CYAN}❓ 未知命令: '{command}'{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}💡 输入 'help' 查看所有可用命令{Style.RESET_ALL}")
                
                # 如果没有选中的代理，直接返回
                if not self.agent_manager.get_current_agent():
                    return True

        except Exception as e:
            print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
            return True

        return False
    
    def _similarity(self, s1: str, s2: str) -> float:
        """计算两个字符串的相似度（简单的编辑距离）"""
        if s1 == s2:
            return 1.0
        
        # 简单的相似度计算
        if len(s1) < len(s2):
            s1, s2 = s2, s1
        
        if len(s2) == 0:
            return 0.0
        
        # 计算公共字符数
        common_chars = sum(1 for c in s2 if c in s1)
        return common_chars / len(s2)
    
    def _get_session_duration(self) -> str:
        """计算会话运行时长"""
        duration = datetime.now() - self.session_start_time
        total_seconds = int(duration.total_seconds())
        
        if total_seconds < 60:
            return f"{total_seconds}秒"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}分{seconds}秒"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}小时{minutes}分"
    
    def _add_to_history(self, command: str):
        """添加命令到历史记录"""
        if command.strip() and command not in ["", "clear", "help"]:
            self.command_history.append(command)
            # 保持历史记录在合理范围内
            if len(self.command_history) > 50:
                self.command_history.pop(0)
    
    def _handle_composite_command(self, command: str, args: str) -> bool:
        """处理复合命令（如 check balance, get balance 等）"""
        if not args:
            print(f"{Fore.YELLOW}💡 请指定要{command}的内容{Style.RESET_ALL}")
            print(f"   例如: {command} balance, {command} orders, {command} markets")
            return True
        
        # 解析子命令
        sub_command = args.lower().strip()
        
        if sub_command in ["balance", "balances", "bal"]:
            return self._handle_balance_command(command)
        elif sub_command in ["order", "orders", "orderbook"]:
            return self._handle_orders_command(command)
        elif sub_command in ["market", "markets", "ticker"]:
            return self._handle_markets_command(command)
        elif sub_command in ["position", "positions", "pos"]:
            return self._handle_positions_command(command)
        elif sub_command in ["history", "hist", "transactions"]:
            return self._handle_history_command(command)
        else:
            print(f"{Fore.YELLOW}❓ 未知的{command}命令: '{sub_command}'{Style.RESET_ALL}")
            print(f"{Fore.CYAN}💡 支持的{command}命令: balance, orders, markets, positions, history{Style.RESET_ALL}")
            return True
    
    def _handle_balance_command(self, command: str) -> bool:
        """处理余额查询命令"""
        current_agent = self.agent_manager.get_current_agent()
        if not current_agent:
            print(f"{Fore.RED}❌ 请先选择代理{Style.RESET_ALL}")
            print(f"   使用 'switch_agent' 命令选择代理")
            return True
        
        print(f"{Fore.CYAN}💰 查询余额...{Style.RESET_ALL}")
        print(f"   代理地址: {current_agent.get('address', 'unknown')}")
        print(f"   网络: {self._format_network_details()}")
        
        # 调用区块链API查询余额
        try:
            # 构建请求数据
            request_data = {
                "message": "check balance",
                "session_id": self.session_id,
                "agent_id": current_agent.get('address'),
                "agent_key": current_agent.get('private_key'),
                "environment": self.agent_manager.get_current_network()
            }
            
            # 发送请求到服务器
            response = self.make_request("/chat", request_data)
            
            if response and "response" in response:
                print(f"\n{Fore.GREEN}✅ 余额查询结果:{Style.RESET_ALL}")
                self.display_response(response.get("response"), response if self.debug else None)
                # 非调试模式下，也简要显示函数调用信息
                if "function_call" in response and response["function_call"] and not self.debug:
                    fc = response["function_call"]
                    fname = fc.get("name", "unknown")
                    fresult = fc.get("result", {})
                    status = fresult.get("success")
                    print(f"   函数调用: {fname} -> {'成功' if status else '失败'}")
                    if isinstance(fresult, dict) and not status and fresult.get("error"):
                        print(f"   错误: {fresult.get('error')}")
            else:
                print(f"{Fore.RED}❌ 查询失败: 服务器无响应{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ 查询失败: {str(e)}{Style.RESET_ALL}")
            print(f"   请确保服务器正在运行并且代理配置正确")
        
        return True
    
    def _handle_orders_command(self, command: str) -> bool:
        """处理订单查询命令"""
        current_agent = self.agent_manager.get_current_agent()
        if not current_agent:
            print(f"{Fore.RED}❌ 请先选择代理{Style.RESET_ALL}")
            print(f"   使用 'switch_agent' 命令选择代理")
            return True
        
        print(f"{Fore.CYAN}📋 查询订单...{Style.RESET_ALL}")
        print(f"   代理地址: {current_agent.get('address', 'unknown')}")
        print(f"   网络: {self._format_network_details()}")
        
        try:
            request_data = {
                "message": "check orders",
                "session_id": self.session_id,
                "agent_id": current_agent.get('address'),
                "agent_key": current_agent.get('private_key'),
                "environment": self.agent_manager.get_current_network()
            }
            
            response = self.make_request("/chat", request_data)
            
            if response and "response" in response:
                print(f"\n{Fore.GREEN}✅ 订单查询结果:{Style.RESET_ALL}")
                self.display_response(response.get("response"), response if self.debug else None)
                if "function_call" in response and response["function_call"] and not self.debug:
                    fc = response["function_call"]
                    fname = fc.get("name", "unknown")
                    print(f"   函数调用: {fname}")
            else:
                print(f"{Fore.RED}❌ 查询失败: 服务器无响应{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ 查询失败: {str(e)}{Style.RESET_ALL}")
        
        return True
    
    def _handle_markets_command(self, command: str) -> bool:
        """处理市场查询命令"""
        current_agent = self.agent_manager.get_current_agent()
        if not current_agent:
            print(f"{Fore.RED}❌ 请先选择代理{Style.RESET_ALL}")
            print(f"   使用 'switch_agent' 命令选择代理")
            return True
        
        print(f"{Fore.CYAN}📊 查询市场数据...{Style.RESET_ALL}")
        print(f"   代理地址: {current_agent.get('address', 'unknown')}")
        print(f"   网络: {self._format_network_details()}")
        
        try:
            request_data = {
                "message": "show markets",
                "session_id": self.session_id,
                "agent_id": current_agent.get('address'),
                "agent_key": current_agent.get('private_key'),
                "environment": self.agent_manager.get_current_network()
            }
            
            response = self.make_request("/chat", request_data)
            
            if response and "response" in response:
                print(f"\n{Fore.GREEN}✅ 市场数据查询结果:{Style.RESET_ALL}")
                self.display_response(response.get("response"), response if self.debug else None)
                if "function_call" in response and response["function_call"] and not self.debug:
                    fc = response["function_call"]
                    fname = fc.get("name", "unknown")
                    print(f"   函数调用: {fname}")
            else:
                print(f"{Fore.RED}❌ 查询失败: 服务器无响应{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ 查询失败: {str(e)}{Style.RESET_ALL}")
        
        return True
    
    def _handle_positions_command(self, command: str) -> bool:
        """处理持仓查询命令"""
        current_agent = self.agent_manager.get_current_agent()
        if not current_agent:
            print(f"{Fore.RED}❌ 请先选择代理{Style.RESET_ALL}")
            print(f"   使用 'switch_agent' 命令选择代理")
            return True
        
        print(f"{Fore.CYAN}📈 查询持仓...{Style.RESET_ALL}")
        print(f"   代理地址: {current_agent.get('address', 'unknown')}")
        print(f"   网络: {self._format_network_details()}")
        
        try:
            request_data = {
                "message": "check positions",
                "session_id": self.session_id,
                "agent_id": current_agent.get('address'),
                "agent_key": current_agent.get('private_key'),
                "environment": self.agent_manager.get_current_network()
            }
            
            response = self.make_request("/chat", request_data)
            
            if response and "response" in response:
                print(f"\n{Fore.GREEN}✅ 持仓查询结果:{Style.RESET_ALL}")
                self.display_response(response.get("response"), response if self.debug else None)
                if "function_call" in response and response["function_call"] and not self.debug:
                    fc = response["function_call"]
                    fname = fc.get("name", "unknown")
                    print(f"   函数调用: {fname}")
            else:
                print(f"{Fore.RED}❌ 查询失败: 服务器无响应{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ 查询失败: {str(e)}{Style.RESET_ALL}")
        
        return True
    
    def _handle_history_command(self, command: str) -> bool:
        """处理历史记录查询命令"""
        current_agent = self.agent_manager.get_current_agent()
        if not current_agent:
            print(f"{Fore.RED}❌ 请先选择代理{Style.RESET_ALL}")
            print(f"   使用 'switch_agent' 命令选择代理")
            return True
        
        print(f"{Fore.CYAN}📜 查询交易历史...{Style.RESET_ALL}")
        print(f"   代理地址: {current_agent.get('address', 'unknown')}")
        print(f"   网络: {self._format_network_details()}")
        
        try:
            request_data = {
                "message": "check history",
                "session_id": self.session_id,
                "agent_id": current_agent.get('address'),
                "agent_key": current_agent.get('private_key'),
                "environment": self.agent_manager.get_current_network()
            }
            
            response = self.make_request("/chat", request_data)
            
            if response and "response" in response:
                print(f"\n{Fore.GREEN}✅ 交易历史查询结果:{Style.RESET_ALL}")
                self.display_response(response.get("response"), response if self.debug else None)
                if "function_call" in response and response["function_call"] and not self.debug:
                    fc = response["function_call"]
                    fname = fc.get("name", "unknown")
                    print(f"   函数调用: {fname}")
            else:
                print(f"{Fore.RED}❌ 查询失败: 服务器无响应{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}❌ 查询失败: {str(e)}{Style.RESET_ALL}")
        
        return True

    def make_request(
        self, endpoint: str, data: Optional[dict] = None, params: Optional[dict] = None
    ) -> dict:
        """Make API request with current agent information"""
        try:
            url = f"{self.api_url.rstrip('/')}/{endpoint.lstrip('/')}"
            headers = {"Content-Type": "application/json", "Accept": "application/json"}

            # Add current agent information to request if available
            current_agent = self.agent_manager.get_current_agent()
            if current_agent and data:
                data["agent_key"] = current_agent["private_key"]
                data["environment"] = self.agent_manager.get_current_network()
                data["agent_id"] = current_agent["address"]
            else:
                return
            response = requests.post(
                url, json=data, params=params, headers=headers, timeout=60
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

    def run(self):
        """Run the enhanced CLI interface"""
        self.display_banner()

        while True:
            try:
                user_input = input(f"{Fore.GREEN}Command: {Style.RESET_ALL}").strip()

                if user_input.lower() == "quit":
                    print(
                        f"\n{Fore.YELLOW}Exiting Injective Chain CLI... 👋{Style.RESET_ALL}"
                    )
                    break

                # Handle 'clear' command
                if user_input.lower() == "clear":
                    self.clear_screen()
                    self.display_banner()
                    continue

                # Split command and arguments
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                # Add command to history
                self._add_to_history(user_input)

                # Handle agent-specific commands
                if self.handle_agent_commands(command, args):
                    continue

                if not self.agent_manager.get_current_agent():
                    print(
                        f"{Fore.RED}Error: No agent selected. Use 'switch_agent' to select an agent.{Style.RESET_ALL}"
                    )
                    continue

                # Start animation before making the request
                self.start_animation()

                try:
                    agent = self.agent_manager.get_current_agent()
                    result = self.make_request(
                        "/chat",
                        {
                            "message": user_input,
                            "session_id": self.session_id,
                            "agent_id": agent["address"],
                            "agent_key": agent["private_key"],
                            "environment": self.agent_manager.get_current_network(),
                        },
                    )

                    # Stop animation before displaying response
                    self.stop_animation()
                    self.display_response(
                        result.get("response"), result if self.debug else None
                    )

                except Exception as e:
                    self.stop_animation()
                    print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")

            except KeyboardInterrupt:
                self.stop_animation()
                print(
                    f"\n{Fore.YELLOW}Exiting Injective Chain CLI... 👋{Style.RESET_ALL}"
                )
                break
            except Exception as e:
                self.stop_animation()
                print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description="Injective Chain CLI Client")
    parser.add_argument("--url", default="http://localhost:5000", help="API URL")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    try:
        cli = InjectiveCLI(args.url, args.debug)
        cli.run()
    except Exception as e:
        print(f"{Fore.RED}Failed to start CLI: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
