#!/usr/bin/env python3
"""
测试余额查询功能
"""

import requests
import json

def test_balance_query():
    """测试余额查询功能"""
    url = "http://localhost:5000/chat"
    
    # 测试数据 - 使用实际的私钥
    test_data = {
        "message": "check balance",
        "session_id": "test_session",
        "agent_id": "inj198jl768fh6y22dg33sk7x9gvyq86n8sd6zaasj",
        "agent_key": "5d8cb33595fa1268adcb42a043a716080a0d8c9952ca763fab0b9bb574395c9d",
        "environment": "testnet"
    }
    
    try:
        print("🔍 测试余额查询功能...")
        print(f"   请求URL: {url}")
        print(f"   代理地址: {test_data['agent_id']}")
        print(f"   网络: {test_data['environment']}")
        
        response = requests.post(url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 请求成功!")
            print(f"   响应状态码: {response.status_code}")
            
            # 检查是否有函数调用
            if "function_call" in result and result["function_call"]:
                print(f"\n🎯 检测到函数调用!")
                function_name = result["function_call"].get("name", "unknown")
                function_result = result["function_call"].get("result", {})
                print(f"   函数名称: {function_name}")
                
                if function_result.get("success"):
                    balances = function_result.get("result", {})
                    if balances:
                        print(f"\n💰 余额信息:")
                        for denom, amount in balances.items():
                            print(f"   {denom}: {amount}")
                    else:
                        print(f"   余额为空")
                else:
                    print(f"   查询失败: {function_result.get('error', '未知错误')}")
                
                print(f"\n📝 AI回复:")
                print(f"   {result.get('response', 'No response')}")
            else:
                print(f"\n⚠️  没有检测到函数调用")
                print(f"   AI回复: {result.get('response', 'No response')}")
        else:
            print(f"\n❌ 请求失败!")
            print(f"   状态码: {response.status_code}")
            print(f"   响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ 连接失败! 请确保服务器正在运行在 http://localhost:5000")
    except requests.exceptions.Timeout:
        print(f"\n❌ 请求超时!")
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    test_balance_query()
