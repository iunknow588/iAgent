#!/usr/bin/env python3
"""
依赖修复脚本 - Injective Agent API
修复项目中的依赖版本冲突问题
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def fix_dependencies():
    """修复依赖问题"""
    print("🚀 开始修复依赖问题...")
    
    # 升级pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "升级pip"):
        return False
    
    # 卸载冲突的包
    conflict_packages = ["urllib3", "chardet", "requests"]
    for package in conflict_packages:
        run_command(f"{sys.executable} -m pip uninstall -y {package}", f"卸载 {package}")
    
    # 重新安装正确版本的包
    packages = [
        "requests>=2.31.0",
        "urllib3>=2.0.0,<3.0.0", 
        "chardet>=5.0.0,<6.0.0",
        "openai",
        "quart",
        "hypercorn",
        "aiohttp",
        "psutil",
        "python-dotenv",
        "pyyaml",
        "injective-py"
    ]
    
    for package in packages:
        if not run_command(f"{sys.executable} -m pip install {package}", f"安装 {package}"):
            return False
    
    print("✅ 依赖修复完成")
    return True

def check_dependencies():
    """检查依赖是否正确安装"""
    print("🔍 检查依赖...")
    
    test_imports = [
        "requests",
        "urllib3", 
        "chardet",
        "openai",
        "quart",
        "hypercorn",
        "aiohttp",
        "psutil",
        "dotenv"
    ]
    
    failed_imports = []
    for module in test_imports:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            print(f"   ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ 以下模块导入失败: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ 所有依赖检查通过")
        return True

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 Injective Agent API 依赖修复工具")
    print("=" * 60)
    
    # 修复依赖
    if not fix_dependencies():
        print("❌ 依赖修复失败")
        return 1
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败")
        return 1
    
    print("\n🎉 依赖修复和检查完成！")
    print("现在可以正常启动服务器了。")
    return 0

if __name__ == "__main__":
    sys.exit(main())
