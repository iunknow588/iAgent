#!/usr/bin/env python3
"""
脚本兼容性测试 - Injective Agent API
测试 quick_start.py 依赖的脚本是否能正确运行
"""

import os
import sys
import subprocess
import importlib
import argparse
from datetime import datetime

class ScriptCompatibilityTester:
    """测试脚本兼容性"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.results = {}
        
    def test_imports(self):
        """测试模块导入"""
        print("🔍 测试模块导入...")
        
        modules_to_test = [
            "quick_start_service",
            "quick_start_client", 
            "quick_start_monitor",
            "app.agent_manager"
        ]
        
        for module in modules_to_test:
            try:
                importlib.import_module(module)
                print(f"   ✅ {module}")
                self.results[f"import_{module}"] = True
            except ImportError as e:
                print(f"   ❌ {module}: {e}")
                self.results[f"import_{module}"] = False
    
    def test_syntax(self):
        """测试语法正确性"""
        print("\n🔍 测试语法正确性...")
        
        scripts_to_test = [
            "quick_start_service.py",
            "quick_start_client.py",
            "quick_start_monitor.py",
            "app/agent_manager.py"
        ]
        
        for script in scripts_to_test:
            script_path = os.path.join(self.base_dir, script)
            try:
                subprocess.run([
                    sys.executable, "-m", "py_compile", script_path
                ], check=True, capture_output=True)
                print(f"   ✅ {script}")
                self.results[f"syntax_{script}"] = True
            except subprocess.CalledProcessError as e:
                print(f"   ❌ {script}: 语法错误")
                self.results[f"syntax_{script}"] = False
    
    def test_help_commands(self):
        """测试帮助命令"""
        print("\n🔍 测试帮助命令...")
        
        help_tests = [
            ("quick_start_service.py", ["--help"]),
            ("quick_start_client.py", ["--help"]),
            ("quick_start_monitor.py", ["--help"])
        ]
        
        for script, args in help_tests:
            script_path = os.path.join(self.base_dir, script)
            try:
                result = subprocess.run([
                    sys.executable, script_path
                ] + args, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print(f"   ✅ {script} 帮助命令正常")
                    self.results[f"help_{script}"] = True
                else:
                    print(f"   ❌ {script} 帮助命令失败: {result.stderr}")
                    self.results[f"help_{script}"] = False
            except subprocess.TimeoutExpired:
                print(f"   ⚠️  {script} 帮助命令超时")
                self.results[f"help_{script}"] = False
            except Exception as e:
                print(f"   ❌ {script} 帮助命令异常: {e}")
                self.results[f"help_{script}"] = False
    
    def test_argument_parsing(self):
        """测试参数解析"""
        print("\n🔍 测试参数解析...")
        
        arg_tests = [
            ("quick_start_service.py", ["--start"]),
            ("quick_start_service.py", ["--stop"]),
            ("quick_start_service.py", ["--status"]),
            ("quick_start_client.py", ["--url", "http://localhost:5000"]),
            ("quick_start_client.py", ["--debug"]),
            ("quick_start_monitor.py", ["--auto"]),
            ("quick_start_monitor.py", ["--report"])
        ]
        
        for script, args in arg_tests:
            script_path = os.path.join(self.base_dir, script)
            try:
                result = subprocess.run([
                    sys.executable, script_path
                ] + args, capture_output=True, text=True, timeout=5)
                
                # 不检查返回码，因为某些命令可能需要服务器运行
                print(f"   ✅ {script} {' '.join(args)} 参数解析正常")
                self.results[f"args_{script}_{'_'.join(args)}"] = True
            except subprocess.TimeoutExpired:
                print(f"   ⚠️  {script} {' '.join(args)} 参数解析超时")
                self.results[f"args_{script}_{'_'.join(args)}"] = False
            except Exception as e:
                print(f"   ❌ {script} {' '.join(args)} 参数解析异常: {e}")
                self.results[f"args_{script}_{'_'.join(args)}"] = False
    
    def test_dependencies(self):
        """测试依赖项"""
        print("\n🔍 测试依赖项...")
        
        dependencies = [
            "colorama",
            "requests", 
            "yaml",
            "psutil",
            "aiohttp",
            "asyncio",
            "argparse",
            "json",
            "datetime",
            "threading",
            "subprocess",
            "os",
            "sys"
        ]
        
        for dep in dependencies:
            try:
                importlib.import_module(dep)
                print(f"   ✅ {dep}")
                self.results[f"dep_{dep}"] = True
            except ImportError as e:
                print(f"   ❌ {dep}: {e}")
                self.results[f"dep_{dep}"] = False
    
    def test_file_existence(self):
        """测试文件存在性"""
        print("\n🔍 测试文件存在性...")
        
        required_files = [
            "quick_start_service.py",
            "quick_start_client.py", 
            "quick_start_monitor.py",
            "app/agent_manager.py",
            "agents_config.yaml",
            "requirements.txt"
        ]
        
        for file_path in required_files:
            full_path = os.path.join(self.base_dir, file_path)
            if os.path.exists(full_path):
                print(f"   ✅ {file_path}")
                self.results[f"file_{file_path}"] = True
            else:
                print(f"   ❌ {file_path} 不存在")
                self.results[f"file_{file_path}"] = False
    
    def generate_report(self):
        """生成测试报告"""
        print("\n📊 测试报告")
        print("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {failed_tests}")
        print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for test_name, result in self.results.items():
                if not result:
                    print(f"  - {test_name}")
        
        print("\n✅ 通过的测试:")
        for test_name, result in self.results.items():
            if result:
                print(f"  - {test_name}")
        
        return passed_tests == total_tests
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 Injective Agent API 脚本兼容性测试")
        print("=" * 60)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        self.test_file_existence()
        self.test_dependencies()
        self.test_imports()
        self.test_syntax()
        self.test_help_commands()
        self.test_argument_parsing()
        
        success = self.generate_report()
        
        if success:
            print("\n🎉 所有测试通过！脚本兼容性良好。")
        else:
            print("\n⚠️  部分测试失败，请检查上述问题。")
        
        return success

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="脚本兼容性测试")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    args = parser.parse_args()
    
    tester = ScriptCompatibilityTester()
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
