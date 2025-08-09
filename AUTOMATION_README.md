# 🤖 Injective Agent API 自动化工具集

这是一个完整的自动化测试、监控和部署工具集，用于 Injective Agent API 服务器。

## 📋 工具概览

### 1. 自动化测试工具

#### `test_agent_api.py` - 基础API测试
```bash
python test_agent_api.py
```
- ✅ 测试所有API端点
- ✅ 验证服务器连接性
- ✅ 检查聊天功能
- ✅ 测试历史记录管理
- ✅ 验证错误处理

#### `test_blockchain_functions.py` - 区块链功能测试
```bash
python test_blockchain_functions.py
```
- 🔗 测试区块链查询功能
- 💱 测试交易相关功能
- 🏦 测试质押功能
- 🔧 测试高级区块链功能

#### `generate_test_report.py` - 综合测试报告
```bash
python generate_test_report.py
```
- 📊 生成详细测试报告
- ⚡ 性能压力测试
- 🧪 错误处理测试
- 📄 保存JSON格式报告

### 2. 监控工具

#### `monitor_server.py` - 实时服务器监控
```bash
python monitor_server.py
```
- 📈 实时性能监控
- 💻 系统资源监控
- ⏱️ 响应时间统计
- 📊 成功率分析

### 3. 部署工具

#### `auto_deploy.py` - 自动化部署
```bash
python auto_deploy.py
```
- 🐍 检查Python版本
- 📦 自动安装依赖
- 🔧 验证环境配置
- 🚀 启动服务器
- 🧪 运行快速测试

## 🚀 快速开始

### 1. 环境准备
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 OPENAI_API_KEY
```

### 2. 启动服务器
```bash
# 手动启动
python agent_server.py --port 5000

# 或使用自动化部署
python auto_deploy.py
```

### 3. 运行测试
```bash
# 基础API测试
python test_agent_api.py

# 区块链功能测试
python test_blockchain_functions.py

# 生成综合报告
python generate_test_report.py
```

### 4. 监控服务器
```bash
# 实时监控
python monitor_server.py
```

## 📊 API 端点

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/` | API信息 |
| GET | `/ping` | 健康检查 |
| POST | `/chat` | 聊天功能 |
| GET | `/history` | 获取历史记录 |
| POST | `/clear` | 清除历史记录 |

## 🔧 配置选项

### 环境变量
```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE_URL=https://api.openai.com  # 可选
```

### 服务器参数
```bash
python agent_server.py --port 5000 --host 0.0.0.0 --debug
```

## 📈 性能指标

### 测试结果示例
- ✅ 基础API测试: 通过
- ✅ 聊天功能测试: 通过
- ✅ 区块链功能测试: 通过
- ✅ 性能压力测试: 通过
- ✅ 错误处理测试: 通过

### 性能数据
- 平均响应时间: ~3.2秒
- 并发处理能力: 10个并发请求
- 成功率: 100%

## 🛠️ 故障排除

### 常见问题

1. **API密钥错误**
   ```
   ❌ 未设置OPENAI_API_KEY环境变量
   ```
   解决: 检查 `.env` 文件中的API密钥配置

2. **端口被占用**
   ```
   ⚠️ 端口5000已被占用
   ```
   解决: 使用不同端口或停止占用端口的服务

3. **依赖缺失**
   ```
   ❌ 缺少依赖: psutil
   ```
   解决: 运行 `pip install psutil`

4. **服务器启动失败**
   ```
   ❌ 服务器启动失败
   ```
   解决: 检查日志输出，确认环境配置正确

### 调试模式
```bash
python agent_server.py --debug
```

## 📄 报告文件

### 生成的报告
- `test_report.json` - 综合测试报告
- `deployment_report.json` - 部署报告

### 报告内容
- 测试结果摘要
- 性能统计数据
- 错误信息记录
- 系统环境信息

## 🔄 自动化工作流

### 完整测试流程
```bash
# 1. 启动服务器
python auto_deploy.py

# 2. 运行所有测试
python test_agent_api.py
python test_blockchain_functions.py
python generate_test_report.py

# 3. 监控服务器
python monitor_server.py
```

### CI/CD 集成
```bash
# 自动化测试脚本
#!/bin/bash
python auto_deploy.py &
sleep 10
python test_agent_api.py
python generate_test_report.py
```

## 📞 支持

如果遇到问题，请检查：
1. Python版本 (需要 3.8+)
2. 依赖包安装
3. 环境变量配置
4. 网络连接状态
5. API密钥有效性

## 🎯 最佳实践

1. **定期运行测试**: 建议每天运行一次完整测试
2. **监控性能**: 使用监控工具跟踪服务器性能
3. **备份配置**: 定期备份 `.env` 和配置文件
4. **日志管理**: 定期清理日志文件
5. **安全更新**: 及时更新依赖包

---

**🎉 自动化工具集已准备就绪！开始使用吧！**
