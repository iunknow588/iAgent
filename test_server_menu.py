#!/usr/bin/env python3
"""
测试服务器管理菜单的修复
"""

import os
import sys
import subprocess
import time

def test_server_menu():
    """测试服务器管理菜单"""
    print("🧪 测试服务器管理菜单修复...")
    
    # 检查服务器是否已经运行
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 5000))
    sock.close()
    
    if result == 0:
        print("✅ 服务器已经在运行")
        print("🎯 现在测试菜单修复...")
        
        # 模拟用户输入：选择1（启动服务器），然后选择1（启动客户端）
        test_input = "1\n1\n"  # 选择启动服务器，然后选择启动客户端
        
        try:
            # 运行quick_start_service.py并模拟输入
            process = subprocess.Popen(
                [sys.executable, "quick_start_service.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=test_input, timeout=30)
            
            print("📋 测试输出:")
            print(stdout)
            
            if "启动客户端" in stdout:
                print("✅ 修复成功！菜单现在提供启动客户端的选项")
            else:
                print("❌ 修复可能不完整")
                
        except subprocess.TimeoutExpired:
            print("⏰ 测试超时")
            process.kill()
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    else:
        print("⚠️  服务器未运行，无法测试菜单修复")
        print("💡 请先启动服务器：python3 quick_start_service.py")

if __name__ == "__main__":
    test_server_menu()
