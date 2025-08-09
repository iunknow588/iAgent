#!/usr/bin/env python3
"""
修复.env文件格式问题
"""

import os
import shutil
from datetime import datetime

def backup_env_file():
    """备份当前的.env文件"""
    if os.path.exists(".env"):
        backup_name = f".env.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(".env", backup_name)
        print(f"✅ 已备份当前配置到: {backup_name}")
        return True
    return False

def fix_env_file():
    """修复.env文件格式"""
    if not os.path.exists(".env"):
        print("❌ 未找到.env文件")
        return False
    
    # 读取当前内容
    with open(".env", "r") as f:
        content = f.read()
    
    # 解析现有配置
    config = {}
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            config[key] = value
    
    # 创建修复后的内容
    fixed_content = """# API配置 - 支持多种API类型
# 使用 SELECTED_MODEL 参数来选择要使用的API

# DeepSeek API配置 (推荐 - 免费额度大)
DEEPSEEK_API_KEY={deepseek_key}
DEEPSEEK_API_BASE_URL=https://api.deepseek.com

# OpenAI API配置 (官方)
OPENAI_API_KEY={openai_key}
OPENAI_API_BASE_URL={openai_url}

# 模型选择参数 (auto, deepseek, openai, chatanywhere)
# auto: 自动选择第一个可用的API
# deepseek: 使用DeepSeek API
# openai: 使用OpenAI API
# chatanywhere: 使用ChatAnywhere API
SELECTED_MODEL={selected_model}

# 区块链配置
NETWORK={network}
INJECTIVE_API_URL={injective_url}
INJECTIVE_MAINNET_API_URL={injective_mainnet_url}

# Account information
ACCOUNT_NAME={account_name}
ACCOUNT_ADDRESS={account_address}
PRIVATE_KEY={private_key}
""".format(
        deepseek_key=config.get('DEEPSEEK_API_KEY', 'your_deepseek_api_key_here'),
        openai_key=config.get('OPENAI_API_KEY', 'your_openai_api_key_here'),
        openai_url=config.get('OPENAI_API_BASE_URL', 'https://api.openai.com'),
        selected_model=config.get('SELECTED_MODEL', 'auto'),
        network=config.get('NETWORK', 'testnet'),
        injective_url=config.get('INJECTIVE_API_URL', 'https://testnet.sentry.lcd.injective.network'),
        injective_mainnet_url=config.get('INJECTIVE_MAINNET_API_URL', 'https://sentry.lcd.injective.network'),
        account_name=config.get('ACCOUNT_NAME', 'wisely'),
        account_address=config.get('ACCOUNT_ADDRESS', 'your_account_address_here'),
        private_key=config.get('PRIVATE_KEY', 'your_private_key_here')
    )
    
    # 写入修复后的内容
    try:
        with open(".env", "w") as f:
            f.write(fixed_content)
        print("✅ .env文件已修复")
        return True
    except Exception as e:
        print(f"❌ 修复.env文件失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 修复.env文件格式")
    print("="*30)
    
    # 备份当前配置
    if not backup_env_file():
        return
    
    # 修复文件
    if fix_env_file():
        print("\n📋 修复完成！")
        print("\n💡 现在您可以:")
        print("   1. 编辑 .env 文件，设置 SELECTED_MODEL=deepseek 来使用DeepSeek API")
        print("   2. 或者设置 SELECTED_MODEL=openai 来使用OpenAI API")
        print("   3. 或者设置 SELECTED_MODEL=auto 来自动选择")
        print("\n🎯 示例配置:")
        print("   SELECTED_MODEL=deepseek  # 使用DeepSeek API")
        print("   SELECTED_MODEL=openai    # 使用OpenAI API")
        print("   SELECTED_MODEL=auto      # 自动选择")
    else:
        print("❌ 修复失败")

if __name__ == "__main__":
    main()
