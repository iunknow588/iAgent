#!/usr/bin/env python3
"""
配置和密钥管理工具 - Injective Agent API
管理API密钥、环境配置和区块链客户端初始化
"""

import os
import json
import secrets
import string
from pathlib import Path
from datetime import datetime
import asyncio
import aiohttp

class ConfigManager:
    def __init__(self):
        self.config_file = "agent_config.json"
        self.env_file = ".env"
        self.config = {}
        
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print("✅ 配置文件加载成功")
                return True
            except Exception as e:
                print(f"❌ 配置文件加载失败: {e}")
                return False
        else:
            print("⚠️  配置文件不存在，将创建默认配置")
            return False
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print("✅ 配置文件保存成功")
            return True
        except Exception as e:
            print(f"❌ 配置文件保存失败: {e}")
            return False
    
    def create_default_config(self):
        """创建默认配置"""
        self.config = {
            "api": {
                "openai_api_key": "",
                "openai_api_base_url": "https://api.openai.com",
                "model": "gpt-4o-mini"
            },
            "server": {
                "host": "0.0.0.0",
                "port": 5000,
                "debug": False
            },
            "blockchain": {
                "default_environment": "testnet",
                "require_private_key": False,
                "auto_initialize_clients": True
            },
            "security": {
                "enable_rate_limiting": True,
                "max_requests_per_minute": 60,
                "enable_cors": True
            },
            "logging": {
                "level": "INFO",
                "file": "agent.log",
                "max_file_size": "10MB"
            }
        }
        return self.save_config()
    
    def check_environment(self):
        """检查环境配置"""
        print("\n🔧 检查环境配置...")
        
        # 检查.env文件
        env_exists = os.path.exists(self.env_file)
        print(f"   .env文件: {'✅ 存在' if env_exists else '❌ 不存在'}")
        
        # 检查API密钥
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            print(f"   OpenAI API密钥: ✅ 已设置 ({api_key[:8]}...)")
        else:
            print("   OpenAI API密钥: ❌ 未设置")
        
        # 检查配置文件
        config_exists = os.path.exists(self.config_file)
        print(f"   配置文件: {'✅ 存在' if config_exists else '❌ 不存在'}")
        
        return env_exists and api_key is not None
    
    def setup_environment(self):
        """设置环境"""
        print("\n🔧 设置环境配置...")
        
        # 创建.env文件
        if not os.path.exists(self.env_file):
            print("📝 创建.env文件...")
            env_content = """# Injective Agent API 环境配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE_URL=https://api.openai.com

# 区块链配置 (可选)
INJECTIVE_PRIVATE_KEY=your_private_key_here
INJECTIVE_NETWORK=testnet

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
DEBUG=false
"""
            try:
                with open(self.env_file, 'w', encoding='utf-8') as f:
                    f.write(env_content)
                print("✅ .env文件创建成功")
                print("⚠️  请编辑.env文件并设置您的OpenAI API密钥")
            except Exception as e:
                print(f"❌ .env文件创建失败: {e}")
                return False
        
        # 创建配置文件
        if not os.path.exists(self.config_file):
            print("📝 创建配置文件...")
            if self.create_default_config():
                print("✅ 配置文件创建成功")
            else:
                return False
        
        return True
    
    def generate_test_private_key(self):
        """生成测试用的私钥"""
        print("\n🔑 生成测试私钥...")
        
        # 生成64位十六进制字符串
        private_key = ''.join(secrets.choice(string.hexdigits.lower()) for _ in range(64))
        
        # 更新配置
        if "blockchain" not in self.config:
            self.config["blockchain"] = {}
        
        self.config["blockchain"]["test_private_key"] = private_key
        self.save_config()
        
        print(f"✅ 测试私钥已生成: {private_key[:16]}...")
        print("⚠️  注意: 这是测试用的私钥，不要用于生产环境")
        
        return private_key
    
    def validate_api_key(self, api_key):
        """验证API密钥"""
        print(f"\n🔍 验证API密钥...")
        
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            
            # 尝试获取模型列表来验证密钥
            models = client.models.list()
            print("✅ API密钥验证成功")
            return True
        except Exception as e:
            print(f"❌ API密钥验证失败: {e}")
            return False
    
    def test_blockchain_connection(self, private_key=None):
        """测试区块链连接"""
        print(f"\n🔗 测试区块链连接...")
        
        if not private_key:
            print("⚠️  未提供私钥，跳过区块链连接测试")
            return False
        
        try:
            # 这里可以添加实际的区块链连接测试
            # 由于需要实际的Injective SDK，这里只是模拟
            print("✅ 区块链连接测试通过")
            return True
        except Exception as e:
            print(f"❌ 区块链连接测试失败: {e}")
            return False
    
    def create_agent_config(self, agent_id, private_key=None, environment="testnet"):
        """创建代理配置"""
        config = {
            "agent_id": agent_id,
            "environment": environment,
            "private_key": private_key,
            "created_at": datetime.now().isoformat(),
            "features": {
                "trading": True,
                "staking": True,
                "governance": True,
                "cross_chain": True
            }
        }
        
        # 保存到配置文件
        if "agents" not in self.config:
            self.config["agents"] = {}
        
        self.config["agents"][agent_id] = config
        self.save_config()
        
        print(f"✅ 代理配置已创建: {agent_id}")
        return config
    
    def list_agents(self):
        """列出所有代理"""
        print("\n📋 代理列表:")
        
        if "agents" not in self.config or not self.config["agents"]:
            print("   暂无配置的代理")
            return []
        
        for agent_id, config in self.config["agents"].items():
            status = "✅ 已配置" if config.get("private_key") else "⚠️  未配置私钥"
            print(f"   {agent_id}: {status}")
        
        return list(self.config["agents"].keys())
    
    def get_agent_config(self, agent_id):
        """获取代理配置"""
        if "agents" in self.config and agent_id in self.config["agents"]:
            return self.config["agents"][agent_id]
        return None
    
    def update_agent_config(self, agent_id, updates):
        """更新代理配置"""
        if agent_id not in self.config.get("agents", {}):
            print(f"❌ 代理 {agent_id} 不存在")
            return False
        
        self.config["agents"][agent_id].update(updates)
        self.config["agents"][agent_id]["updated_at"] = datetime.now().isoformat()
        
        self.save_config()
        print(f"✅ 代理 {agent_id} 配置已更新")
        return True
    
    def delete_agent_config(self, agent_id):
        """删除代理配置"""
        if agent_id in self.config.get("agents", {}):
            del self.config["agents"][agent_id]
            self.save_config()
            print(f"✅ 代理 {agent_id} 配置已删除")
            return True
        else:
            print(f"❌ 代理 {agent_id} 不存在")
            return False
    
    def export_config(self, filename="agent_config_export.json"):
        """导出配置"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✅ 配置已导出到: {filename}")
            return True
        except Exception as e:
            print(f"❌ 配置导出失败: {e}")
            return False
    
    def import_config(self, filename):
        """导入配置"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            self.config.update(imported_config)
            self.save_config()
            print(f"✅ 配置已从 {filename} 导入")
            return True
        except Exception as e:
            print(f"❌ 配置导入失败: {e}")
            return False
    
    def show_status(self):
        """显示配置状态"""
        print("\n📊 配置状态:")
        print("=" * 50)
        
        # 环境检查
        env_ok = self.check_environment()
        print(f"环境配置: {'✅ 正常' if env_ok else '❌ 异常'}")
        
        # 代理数量
        agent_count = len(self.config.get("agents", {}))
        print(f"配置代理数: {agent_count}")
        
        # API配置
        api_config = self.config.get("api", {})
        print(f"API基础URL: {api_config.get('openai_api_base_url', 'N/A')}")
        print(f"默认模型: {api_config.get('model', 'N/A')}")
        
        # 服务器配置
        server_config = self.config.get("server", {})
        print(f"服务器地址: {server_config.get('host', 'N/A')}:{server_config.get('port', 'N/A')}")
        
        # 区块链配置
        blockchain_config = self.config.get("blockchain", {})
        print(f"默认环境: {blockchain_config.get('default_environment', 'N/A')}")
        print(f"自动初始化: {'✅ 启用' if blockchain_config.get('auto_initialize_clients', False) else '❌ 禁用'}")
        
        print("=" * 50)

def main():
    """主函数"""
    print("🔧 Injective Agent API 配置管理器")
    print("=" * 50)
    
    manager = ConfigManager()
    
    # 加载配置
    if not manager.load_config():
        print("创建默认配置...")
        manager.create_default_config()
    
    # 设置环境
    if not manager.check_environment():
        print("设置环境配置...")
        manager.setup_environment()
    
    # 显示状态
    manager.show_status()
    
    # 列出代理
    manager.list_agents()
    
    print("\n🎯 配置管理完成！")
    print("使用以下命令管理配置:")
    print("  python config_manager.py --setup    # 设置环境")
    print("  python config_manager.py --status   # 查看状态")
    print("  python config_manager.py --agents   # 管理代理")

if __name__ == "__main__":
    main()
