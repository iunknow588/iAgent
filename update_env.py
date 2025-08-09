#!/usr/bin/env python3
"""
更新.env文件，添加DeepSeek API支持
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

def read_current_env():
    """读取当前的.env文件内容"""
    if not os.path.exists(".env"):
        print("❌ 未找到.env文件")
        return None
    
    with open(".env", "r") as f:
        return f.read()

def update_env_content(content):
    """更新.env文件内容，添加DeepSeek API支持"""
    lines = content.split('\n')
    updated_lines = []
    
    # 添加头部注释
    updated_lines.append("# API配置 - 支持多种API类型")
    updated_lines.append("# 使用 SELECTED_MODEL 参数来选择要使用的API")
    updated_lines.append("")
    
    # 添加DeepSeek配置
    updated_lines.append("# DeepSeek API配置 (推荐 - 免费额度大)")
    updated_lines.append("DEEPSEEK_API_KEY=your_deepseek_api_key_here")
    updated_lines.append("DEEPSEEK_API_BASE_URL=https://api.deepseek.com")
    updated_lines.append("")
    
    # 处理现有的OpenAI配置
    openai_key_found = False
    openai_url_found = False
    
    for line in lines:
        line = line.strip()
        if line.startswith("OPENAI_API_KEY="):
            updated_lines.append(f"# OpenAI API配置 (官方)")
            updated_lines.append(line)
            openai_key_found = True
        elif line.startswith("OPENAI_API_BASE_URL="):
            updated_lines.append(line)
            openai_url_found = True
        elif line.startswith("#") and "API" in line:
            # 跳过旧的API注释
            continue
        elif line.startswith("NETWORK=") or line.startswith("INJECTIVE_") or line.startswith("ACCOUNT_") or line.startswith("PRIVATE_KEY="):
            # 区块链和账户配置
            if not openai_key_found:
                updated_lines.append("")
                updated_lines.append("# OpenAI API配置 (官方)")
                updated_lines.append("OPENAI_API_KEY=your_openai_api_key_here")
                updated_lines.append("OPENAI_API_BASE_URL=https://api.chatanywhere.tech")
                updated_lines.append("")
                openai_key_found = True
                openai_url_found = True
            
            updated_lines.append("")
            updated_lines.append("# 区块链配置")
            updated_lines.append(line)
        elif line and not line.startswith("#"):
            # 其他配置项
            updated_lines.append(line)
    
    # 添加模型选择参数
    if not any("SELECTED_MODEL=" in line for line in updated_lines):
        updated_lines.append("")
        updated_lines.append("# 模型选择参数 (auto, deepseek, openai, chatanywhere)")
        updated_lines.append("# auto: 自动选择第一个可用的API")
        updated_lines.append("# deepseek: 使用DeepSeek API")
        updated_lines.append("# openai: 使用OpenAI API")
        updated_lines.append("# chatanywhere: 使用ChatAnywhere API")
        updated_lines.append("SELECTED_MODEL=auto")
    
    return '\n'.join(updated_lines)

def write_env_file(content):
    """写入更新后的.env文件"""
    try:
        with open(".env", "w") as f:
            f.write(content)
        print("✅ .env文件已更新")
        return True
    except Exception as e:
        print(f"❌ 写入.env文件失败: {e}")
        return False

def show_instructions():
    """显示配置说明"""
    print("\n" + "="*60)
    print("🔑 DeepSeek API 配置说明")
    print("="*60)
    
    print("\n📋 步骤1: 获取DeepSeek API密钥")
    print("   1. 访问 https://platform.deepseek.com/api_keys")
    print("   2. 注册或登录账户")
    print("   3. 创建新的API密钥")
    
    print("\n📋 步骤2: 更新.env文件")
    print("   1. 编辑 .env 文件")
    print("   2. 将 'your_deepseek_api_key_here' 替换为您的实际DeepSeek API密钥")
    print("   3. 设置 SELECTED_MODEL 参数来选择要使用的API")
    print("   4. 保存文件")
    
    print("\n📋 步骤3: 配置模型选择")
    print("   在 .env 文件中设置 SELECTED_MODEL 参数:")
    print("   - SELECTED_MODEL=deepseek  # 使用DeepSeek API")
    print("   - SELECTED_MODEL=openai    # 使用OpenAI API")
    print("   - SELECTED_MODEL=chatanywhere  # 使用ChatAnywhere API")
    print("   - SELECTED_MODEL=auto      # 自动选择第一个可用的API")
    
    print("\n📋 步骤4: 重启服务")
    print("   1. 停止服务器: python3 quick_start_service.py (选择3)")
    print("   2. 启动服务器: python3 quick_start_service.py (选择1)")
    print("   3. 启动客户端: python3 quick_start_client.py")
    
    print("\n💡 提示:")
    print("   - 使用 SELECTED_MODEL 参数来手动选择API")
    print("   - 如果指定的API不可用，系统会提示错误")
    print("   - 可以随时修改 SELECTED_MODEL 来切换API")
    print("   - 建议先测试API连接再正式使用")

def main():
    """主函数"""
    print("🚀 更新.env文件 - 添加DeepSeek API支持")
    print("="*50)
    
    # 备份当前配置
    if not backup_env_file():
        return
    
    # 读取当前配置
    current_content = read_current_env()
    if not current_content:
        return
    
    # 更新配置
    updated_content = update_env_content(current_content)
    
    # 写入更新后的配置
    if write_env_file(updated_content):
        print("\n📋 更新完成！")
        show_instructions()
        
        print(f"\n🎯 下一步操作:")
        print(f"   1. 编辑 .env 文件，添加您的DeepSeek API密钥")
        print(f"   2. 重启服务器以应用新配置")
        print(f"   3. 测试API连接")
    else:
        print("❌ 更新失败")

if __name__ == "__main__":
    main()
