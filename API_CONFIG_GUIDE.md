# 🔑 API配置指南

## 🚨 当前问题

您遇到的错误是因为使用了免费的 `api.chatanywhere.tech` API，该服务每天只允许5次请求。

## 🎯 解决方案

### 方案1：使用官方OpenAI API密钥（推荐）

1. **获取API密钥**：
   - 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
   - 登录或注册账户
   - 创建新的API密钥

2. **更新配置文件**：
   ```bash
   # 编辑 .env 文件
   nano .env
   ```

3. **修改配置**：
   ```env
   # 将您的OpenAI API密钥替换这里
   OPENAI_API_KEY=your_openai_api_key_here
   
   # 使用官方OpenAI API
   OPENAI_API_BASE_URL=https://api.openai.com
   ```

### 方案2：使用其他API提供商

如果您不想使用官方OpenAI API，可以考虑：

1. **Azure OpenAI**：
   ```env
   OPENAI_API_BASE_URL=https://your-resource-name.openai.azure.com
   OPENAI_API_KEY=your-azure-api-key
   ```

2. **其他兼容的API提供商**：
   - Anthropic Claude
   - Google Gemini
   - 其他兼容OpenAI API的服务

### 方案3：等待重置（临时解决）

如果您想继续使用当前的免费API：
- 等待到第二天00:00后自动重置
- 每天限制5次请求

## 🔧 配置步骤

1. **备份当前配置**：
   ```bash
   cp .env .env.backup
   ```

2. **编辑配置文件**：
   ```bash
   nano .env
   ```

3. **更新API密钥**：
   ```env
   OPENAI_API_KEY=your_new_api_key_here
   OPENAI_API_BASE_URL=https://api.openai.com
   ```

4. **重启服务器**：
   ```bash
   # 停止当前服务器
   python3 quick_start_service.py
   # 选择3停止服务器
   
   # 重新启动服务器
   python3 quick_start_service.py
   # 选择1启动服务器
   ```

## 📊 费用说明

### OpenAI官方API
- **GPT-4o**：约 $0.005 / 1K tokens（输入），$0.015 / 1K tokens（输出）
- **GPT-3.5-turbo**：约 $0.0005 / 1K tokens（输入），$0.0015 / 1K tokens（输出）

### 免费替代方案
- **ChatAnywhere**：每天5次免费请求
- **其他免费API**：通常有类似的限制

## 🛠️ 故障排除

### 常见问题

1. **API密钥无效**：
   - 检查密钥是否正确复制
   - 确认密钥是否有效

2. **网络连接问题**：
   - 检查网络连接
   - 确认防火墙设置

3. **配额超限**：
   - 检查API使用量
   - 考虑升级计划

### 测试配置

配置完成后，可以运行测试：

```bash
# 测试API连接
python3 test_agent_api.py
```

## 📞 获取帮助

如果遇到问题：
1. 查看 [OpenAI文档](https://platform.openai.com/docs)
2. 检查 [项目README](README.md)
3. 提交 [GitHub Issue](https://github.com/your-repo/issues)
