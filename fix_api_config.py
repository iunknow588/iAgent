#!/usr/bin/env python3
"""
API配置修复工具
帮助用户快速解决API限制问题
"""

import os
import sys
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

def check_current_config():
    """检查当前配置"""
    print("🔍 检查当前配置...")
    
    if not os.path.exists(".env"):
        print("❌ 未找到.env文件")
        return False
    
    with open(".env", "r") as f:
        content = f.read()
    
    if "api.chatanywhere.tech" in content:
        print("⚠️  检测到使用免费API (api.chatanywhere.tech)")
        print("   该API每天限制5次请求")
        return True
    elif "api.deepseek.com" in content or "DEEPSEEK_API_KEY" in content:
        print("✅ 检测到使用DeepSeek API")
        return True
    elif "api.openai.com" in content:
        print("✅ 检测到使用官方OpenAI API")
        return True
    else:
        print("❓ 未知的API配置")
        return False

def create_new_env_template():
    """创建新的.env模板"""
    template = """# API配置 - 请选择一种API类型

# 方案1: DeepSeek API (推荐 - 免费额度大)
API_TYPE=deepseek
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_API_BASE_URL=https://api.deepseek.com

# 方案2: OpenAI API (官方)
# API_TYPE=openai
# OPENAI_API_KEY=your_openai_api_key_here
# OPENAI_API_BASE_URL=https://api.openai.com

# 方案3: ChatAnywhere API (免费但限制多)
# API_TYPE=chatanywhere
# OPENAI_API_KEY=your_chatanywhere_api_key_here
# OPENAI_API_BASE_URL=https://api.chatanywhere.tech

# 区块链配置
NETWORK=testnet
INJECTIVE_API_URL=https://testnet.sentry.lcd.injective.network
INJECTIVE_MAINNET_API_URL=https://sentry.lcd.injective.network

# Account information
ACCOUNT_NAME=wisely
ACCOUNT_ADDRESS=your_account_address_here
# Wisely account private key (exported from injectived)
PRIVATE_KEY=your_private_key_here
"""
    
    with open(".env.new", "w") as f:
        f.write(template)
    
    print("✅ 已创建新的.env模板: .env.new")
    print("💡 请编辑 .env.new 文件，选择API类型并添加相应的API密钥")

def show_instructions():
    """显示配置说明"""
    print("\n" + "="*60)
    print("🔑 API配置修复指南")
    print("="*60)
    
    print("\n📋 方案1: DeepSeek API (推荐)")
    print("   1. 访问 https://platform.deepseek.com/api_keys")
    print("   2. 注册或登录账户")
    print("   3. 创建新的API密钥")
    print("   4. 在 .env.new 中设置:")
    print("      API_TYPE=deepseek")
    print("      DEEPSEEK_API_KEY=your_deepseek_api_key_here")
    
    print("\n📋 方案2: OpenAI API (官方)")
    print("   1. 访问 https://platform.openai.com/api-keys")
    print("   2. 登录或注册账户")
    print("   3. 创建新的API密钥")
    print("   4. 在 .env.new 中设置:")
    print("      API_TYPE=openai")
    print("      OPENAI_API_KEY=your_openai_api_key_here")
    
    print("\n📋 方案3: ChatAnywhere API (免费但限制多)")
    print("   1. 访问 https://api.chatanywhere.tech")
    print("   2. 注册账户获取免费API密钥")
    print("   3. 在 .env.new 中设置:")
    print("      API_TYPE=chatanywhere")
    print("      OPENAI_API_KEY=your_chatanywhere_api_key_here")
    
    print("\n📋 步骤2: 更新配置文件")
    print("   1. 编辑 .env.new 文件")
    print("   2. 选择一种API类型并取消注释相应配置")
    print("   3. 将 'your_xxx_api_key_here' 替换为您的实际API密钥")
    print("   4. 保存文件")
    
    print("\n📋 步骤3: 应用新配置")
    print("   1. 备份当前配置: cp .env .env.backup")
    print("   2. 应用新配置: mv .env.new .env")
    print("   3. 重启服务器")
    
    print("\n📋 步骤4: 重启服务")
    print("   1. 停止服务器: python3 quick_start_service.py (选择3)")
    print("   2. 启动服务器: python3 quick_start_service.py (选择1)")
    print("   3. 启动客户端: python3 quick_start_client.py")

def main():
    """主函数"""
    print("🚀 API配置修复工具")
    print("="*40)
    
    # 检查当前配置
    if check_current_config():
        print("\n🎯 检测到API限制问题")
        
        # 备份当前配置
        if backup_env_file():
            print("✅ 配置已备份")
        
        # 创建新模板
        create_new_env_template()
        
        # 显示说明
        show_instructions()
        
        print("\n💡 提示:")
        print("   - 如果您不想更换API，可以等待到明天00:00后继续使用")
        print("   - 官方OpenAI API费用很低，建议使用官方API")
        print("   - 更多信息请查看 API_CONFIG_GUIDE.md")
        
    else:
        print("❌ 无法检测到当前配置")
        print("💡 请手动检查 .env 文件")

if __name__ == "__main__":
    main()
