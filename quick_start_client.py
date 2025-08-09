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
        self.agent_manager = AgentManager()

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system("cls" if os.name == "nt" else "clear")

    def start_animation(self):
        """Start the animation in a new thread"""
        self.animation_stop = False
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
        print(f"Current Network: {self.agent_manager.get_current_network().upper()}")

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
            else:
                # 检查是否是拼写错误
                known_commands = ["help", "ping", "switch_network", "create_agent", "delete_agent", "switch_agent", "list_agents"]
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
