#!/usr/bin/env python3
"""
🔐 安全密钥泄露检查脚本
用于检查代码中是否存在密钥泄露的安全问题
"""

import os
import re
import glob
from pathlib import Path

class SecurityChecker:
    def __init__(self):
        self.issues = []
        self.sensitive_patterns = {
            'private_key': r'private_key["\']?\s*:\s*["\']?[a-f0-9]{64}["\']?',
            'wallet_address': r'address["\']?\s*:\s*["\']?inj1[a-zA-Z0-9]{38}["\']?',
            'openai_api_key': r'sk-[a-zA-Z0-9]{48}',
            'github_token': r'gh[oprst]_[A-Za-z0-9_]{36}',
            'slack_token': r'xox[abp]-\w+',
            'google_api_key': r'AIza[0-9A-Za-z\-_]{35}',
            'aws_access_key': r'AKIA[0-9A-Z]{16}',
            'aws_secret_key': r'[0-9]{12}:AWS4-HMAC-SHA256',
            'google_oauth_token': r'ya29\.[0-9A-Za-z\-_]+',
            'google_oauth_refresh': r'1//[0-9A-Za-z\-_]{35}',
            'google_oauth_code': r'4/[0-9A-Za-z\-_]{35}',
            'google_client_id': r'[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com',
        }
        
        self.safe_patterns = {
            'placeholder': r'<[^>]+>',
            'your_.*_here': r'your_.*_here',
            'example': r'example',
            'template': r'template',
        }
        
        self.ignored_extensions = {
            '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe',
            '.log', '.tmp', '.cache', '.git', '__pycache__'
        }
        
        self.ignored_dirs = {
            '.git', '__pycache__', 'node_modules', 'venv', 'env',
            '.venv', '.env', 'build', 'dist', 'target'
        }

    def is_ignored_file(self, file_path):
        """检查文件是否应该被忽略"""
        path = Path(file_path)
        
        # 检查扩展名
        if path.suffix in self.ignored_extensions:
            return True
            
        # 检查目录名
        for part in path.parts:
            if part in self.ignored_dirs:
                return True
                
        return False

    def check_file(self, file_path):
        """检查单个文件中的敏感信息"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
            for line_num, line in enumerate(lines, 1):
                for pattern_name, pattern in self.sensitive_patterns.items():
                    matches = re.findall(pattern, line, re.IGNORECASE)
                    if matches:
                        # 检查是否是安全的占位符
                        is_safe = False
                        for safe_pattern in self.safe_patterns.values():
                            if re.search(safe_pattern, line, re.IGNORECASE):
                                is_safe = True
                                break
                        
                        if not is_safe:
                            self.issues.append({
                                'file': file_path,
                                'line': line_num,
                                'pattern': pattern_name,
                                'content': line.strip(),
                                'severity': 'HIGH' if 'private_key' in pattern_name else 'MEDIUM'
                            })
                            
        except Exception as e:
            print(f"⚠️  无法读取文件 {file_path}: {e}")

    def scan_directory(self, directory='.'):
        """扫描目录中的所有文件"""
        print(f"🔍 开始扫描目录: {os.path.abspath(directory)}")
        
        for root, dirs, files in os.walk(directory):
            # 跳过忽略的目录
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                if not self.is_ignored_file(file_path):
                    self.check_file(file_path)

    def generate_report(self):
        """生成安全检查报告"""
        if not self.issues:
            print("✅ 未发现安全风险！")
            return
            
        print(f"\n🚨 发现 {len(self.issues)} 个潜在安全问题：")
        print("=" * 80)
        
        # 按严重程度分组
        high_issues = [i for i in self.issues if i['severity'] == 'HIGH']
        medium_issues = [i for i in self.issues if i['severity'] == 'MEDIUM']
        
        if high_issues:
            print(f"\n🔴 高风险问题 ({len(high_issues)} 个):")
            for issue in high_issues:
                print(f"   📁 {issue['file']}:{issue['line']}")
                print(f"   🚨 {issue['pattern']}: {issue['content']}")
                print()
                
        if medium_issues:
            print(f"\n🟡 中风险问题 ({len(medium_issues)} 个):")
            for issue in medium_issues:
                print(f"   📁 {issue['file']}:{issue['line']}")
                print(f"   ⚠️  {issue['pattern']}: {issue['content']}")
                print()
        
        print("=" * 80)
        print("💡 建议:")
        print("   1. 立即检查高风险问题")
        print("   2. 将敏感信息移到环境变量中")
        print("   3. 使用占位符替换硬编码的密钥")
        print("   4. 检查 .gitignore 配置")
        print("   5. 查看 SECURITY_GUIDE.md 获取详细指导")

def main():
    """主函数"""
    print("🔐 Injective Agent 安全密钥泄露检查")
    print("=" * 50)
    
    checker = SecurityChecker()
    
    # 扫描当前目录
    checker.scan_directory()
    
    # 生成报告
    checker.generate_report()
    
    # 检查 .gitignore 配置
    print("\n📋 .gitignore 配置检查:")
    gitignore_path = '.gitignore'
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            content = f.read()
            if 'agents_config.yaml' in content:
                print("   ✅ agents_config.yaml 已在 .gitignore 中")
            else:
                print("   ❌ agents_config.yaml 未在 .gitignore 中")
                
            if '.env' in content:
                print("   ✅ .env 已在 .gitignore 中")
            else:
                print("   ❌ .env 未在 .gitignore 中")
    else:
        print("   ❌ 未找到 .gitignore 文件")

if __name__ == "__main__":
    main()
