# 🔍 DeepSeek API 配置指南

## 🎯 为什么选择 DeepSeek API？

DeepSeek 是一个强大的 AI 模型提供商，提供以下优势：

- ✅ **免费额度大**：每月有大量免费请求额度
- ✅ **性能优秀**：模型性能接近 GPT-4
- ✅ **价格实惠**：付费计划价格合理
- ✅ **兼容性好**：完全兼容 OpenAI API 格式

## 🔑 获取 DeepSeek API 密钥

### 步骤1：注册账户
1. 访问 [DeepSeek Platform](https://platform.deepseek.com)
2. 点击 "Sign Up" 注册新账户
3. 验证邮箱地址

### 步骤2：创建 API 密钥
1. 登录后进入 [API Keys](https://platform.deepseek.com/api_keys) 页面
2. 点击 "Create API Key"
3. 输入密钥名称（如：iAgent）
4. 复制生成的 API 密钥

### 步骤3：查看免费额度
1. 在 [Usage](https://platform.deepseek.com/usage) 页面查看当前使用情况
2. 确认免费额度是否足够

## ⚙️ 配置 DeepSeek API

### 方法1：使用配置工具（推荐）

```bash
# 运行配置修复工具
python3 fix_api_config.py
```

然后按照提示选择 DeepSeek API 并输入您的密钥。

### 方法2：手动配置

1. **备份当前配置**：
   ```bash
   cp .env .env.backup
   ```

2. **编辑 .env 文件**：
   ```bash
   nano .env
   ```

3. **添加 DeepSeek 配置**：
   ```env
   # DeepSeek API 配置
   API_TYPE=deepseek
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   DEEPSEEK_API_BASE_URL=https://api.deepseek.com
   
   # 区块链配置
   NETWORK=testnet
   INJECTIVE_API_URL=https://testnet.sentry.lcd.injective.network
   INJECTIVE_MAINNET_API_URL=https://sentry.lcd.injective.network
   
   # Account information
   ACCOUNT_NAME=wisely
   ACCOUNT_ADDRESS=your_account_address_here
   PRIVATE_KEY=your_private_key_here
   ```

## 🚀 重启服务

配置完成后，需要重启服务：

```bash
# 1. 停止当前服务器
python3 quick_start_service.py
# 选择 3 停止服务器

# 2. 启动服务器
python3 quick_start_service.py
# 选择 1 启动服务器

# 3. 启动客户端
python3 quick_start_client.py
```

## 🧪 测试配置

配置完成后，可以运行测试：

```bash
# 测试 API 连接
python3 test_agent_api.py

# 或者直接使用客户端测试
python3 quick_start_client.py
```

## 📊 DeepSeek API 费用

### 免费计划
- **每月免费额度**：通常有大量免费请求
- **模型**：deepseek-chat
- **限制**：可能有速率限制

### 付费计划
- **价格**：比 OpenAI 更实惠
- **额度**：根据计划不同
- **支持**：优先支持

## 🛠️ 故障排除

### 常见问题

1. **API 密钥无效**：
   ```
   ❌ No DeepSeek API key found
   ```
   **解决**：检查 `DEEPSEEK_API_KEY` 是否正确设置

2. **网络连接问题**：
   ```
   ❌ API request failed
   ```
   **解决**：检查网络连接和防火墙设置

3. **模型名称错误**：
   ```
   ❌ Model not found
   ```
   **解决**：确保使用 `deepseek-chat` 模型名称

4. **配额超限**：
   ```
   ❌ Rate limit exceeded
   ```
   **解决**：检查使用量，考虑升级计划

### 调试模式

启用调试模式查看详细信息：

```bash
# 启动调试模式
python3 quick_start_client.py --debug
```

## 📞 获取帮助

如果遇到问题：

1. **查看 DeepSeek 文档**：[https://platform.deepseek.com/docs](https://platform.deepseek.com/docs)
2. **检查项目 README**：[README.md](README.md)
3. **提交 GitHub Issue**：[https://github.com/your-repo/issues](https://github.com/your-repo/issues)

## 🔄 切换回其他 API

如果需要切换回其他 API：

1. **编辑 .env 文件**：
   ```bash
   nano .env
   ```

2. **修改 API_TYPE**：
   ```env
   # 切换到 OpenAI
   API_TYPE=openai
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_API_BASE_URL=https://api.openai.com
   
   # 或切换到 ChatAnywhere
   API_TYPE=chatanywhere
   OPENAI_API_KEY=your_chatanywhere_api_key_here
   OPENAI_API_BASE_URL=https://api.chatanywhere.tech
   ```

3. **重启服务**：
   ```bash
   python3 quick_start_service.py
   ```

---

**🎉 享受使用 DeepSeek API！**
