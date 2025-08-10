# 📋 配置管理策略说明

## 🎯 配置管理方式

本项目采用**本地明文配置 + Git忽略**的策略，既保证了开发便利性，又确保了安全性。

## 📁 文件分类

### 1. 🔒 本地配置文件（不上传Git）
- `agents_config.yaml` - 包含真实私钥的代理配置
- `.env` - 环境变量文件
- 任何包含真实密钥的配置文件

### 2. 📚 模板和示例文件（上传Git）
- `agents_config_template.yaml` - 配置模板
- `env_example.txt` - 环境变量示例
- `SECURITY_GUIDE.md` - 安全指南

## 🛡️ 安全机制

### Git忽略规则
```gitignore
# Blockchain private keys and wallet configs
agents_config.yaml          # 忽略真实配置文件
wallet_config.yaml          # 忽略钱包配置
*_wallet_config.yaml        # 忽略任何钱包配置
*_private_key*             # 忽略包含私钥的文件
*_wallet_private_key*      # 忽略钱包私钥文件
```

### 工作原理
1. **本地开发**: 您可以在 `agents_config.yaml` 中存储真实的私钥和地址
2. **Git提交**: 该文件被 `.gitignore` 忽略，不会上传到仓库
3. **团队协作**: 其他开发者使用模板文件创建自己的配置

## 🔧 使用流程

### 首次设置
```bash
# 1. 复制配置模板
cp agents_config_template.yaml agents_config.yaml

# 2. 编辑配置文件，填入真实信息
nano agents_config.yaml

# 3. 验证Git状态（应该看不到agents_config.yaml）
git status
```

### 日常使用
```bash
# 直接使用配置文件，无需担心泄露
python3 quick_start.py

# 检查Git状态，确保敏感文件未被跟踪
git status
```

### 添加新代理
```bash
# 在agents_config.yaml中添加新代理配置
# 文件会自动被Git忽略
```

## ✅ 优势

1. **开发便利**: 本地配置立即可用，无需每次输入
2. **安全性**: 敏感信息永远不会上传到Git仓库
3. **团队协作**: 每个开发者都有自己的本地配置
4. **版本控制**: 配置模板和示例文件可以版本控制

## ⚠️ 注意事项

1. **备份重要**: 本地配置文件不会被Git备份，请自行备份
2. **环境隔离**: 不同环境（开发/测试/生产）使用不同的配置文件
3. **定期检查**: 定期运行 `security_check.py` 检查安全状态
4. **权限控制**: 确保本地配置文件有适当的文件权限

## 🚨 紧急情况

如果发现私钥泄露：
1. 立即转移资产到新钱包
2. 废弃泄露的私钥
3. 检查Git历史，确保没有意外提交
4. 更新本地配置文件

## 📞 获取帮助

- 查看 [SECURITY_GUIDE.md](SECURITY_GUIDE.md) 获取详细安全指导
- 运行 `python3 security_check.py` 进行安全检查
- 检查 `.gitignore` 配置是否正确

---

**总结**: 这种配置方式让您可以在本地安全地使用真实配置，同时确保敏感信息永远不会被意外上传到Git仓库。
