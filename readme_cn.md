![Banner!](assets/logo.png)
# Injective Agent 中文文档

欢迎使用基于 OpenAI 的 Injective Chain 智能交易代理。该项目提供了一套完整的自动化工具集，包括智能代理服务器、多代理管理系统、区块链交互模块和完整的测试监控工具，旨在通过自然语言交互为您提供专业的数据驱动交易体验。

## 系统概述

本项目采用模块化架构设计，集成了 OpenAI GPT-4 技术和 Injective Protocol，为用户提供智能化的区块链交易体验。系统支持多代理管理、实时市场分析、自动化交易执行和完整的风险管理机制。

## 项目架构

### 核心组件

* **统一启动工具** (`quick_start.py`)：🚀 集成服务器管理、客户端交互、监控管理的统一入口
* **智能代理服务器** (`agent_server.py`)：基于 Quart 框架的异步 API 服务器
* **代理管理系统** (`app/agent_manager.py`)：多代理配置和私钥管理
* **区块链交互模块** (`injective_functions/`)：完整的 Injective Protocol 功能集
* **配置管理器** (`config_manager.py`)：环境配置和密钥管理
* **自动化工具集**：测试、监控、部署工具

### 区块链功能模块

```
injective_functions/
├── account/           # 账户管理和查询
├── auction/           # 拍卖功能
├── authz/             # 授权管理
├── bank/              # 资金转账和余额查询
├── exchange/          # 交易所功能和订单管理
├── staking/           # 质押和委托
├── token_factory/     # 代币工厂
└── utils/             # 工具函数和初始化器
```

## 核心功能

### 🤖 智能交易功能
* **自然语言交易**：通过对话式界面执行复杂交易策略
* **多市场支持**：现货、衍生品、期权等多种交易类型
* **智能订单管理**：限价单、市价单、批量撤单等
* **实时市场分析**：价格监控、深度分析、趋势预测

### 🛠️ 系统管理功能
* **多代理管理**：支持创建、切换、删除多个交易代理
* **网络切换**：主网/测试网一键切换
* **配置管理**：环境变量、API密钥、代理配置统一管理
* **会话管理**：聊天历史、命令历史、调试模式

### 🔧 自动化工具
* **完整测试套件**：API测试、区块链功能测试、性能测试
* **实时监控**：服务器状态、性能指标、响应时间统计
* **自动化部署**：一键部署、依赖检查、环境验证
* **报告生成**：详细的测试报告和性能分析

## 系统要求

### 基础环境
* **Python 版本**：3.10+ (推荐 3.12)
* **操作系统**：Linux、macOS、Windows (支持 WSL2)
* **内存要求**：最少 4GB RAM，推荐 8GB+
* **网络要求**：稳定的互联网连接，用于访问 OpenAI API 和 Injective Network

### 核心依赖
```txt
openai              # OpenAI GPT-4 API 客户端
quart               # 异步 Web 框架
injective-py        # Injective Protocol Python SDK
hypercorn           # ASGI 服务器
flask               # Web 框架
colorama            # 终端彩色输出
python-dotenv       # 环境变量管理
pyyaml              # YAML 配置文件支持
urllib3>=2.0.0,<3.0.0  # HTTP 客户端
chardet>=5.0.0,<6.0.0  # 字符编码检测
aiohttp             # 异步HTTP客户端
psutil              # 系统进程监控
requests>=2.31.0    # HTTP请求库
```

## 安装指南

### 方案一：统一启动工具（推荐）

1. **克隆仓库并进入目录**：
   ```bash
   git clone https://github.com/InjectiveLabs/iAgent.git
   cd iAgent  
   ```

2. **配置环境变量**：
   ```bash
   # 创建 .env 文件
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   echo "NETWORK=testnet" >> .env
   echo "INJECTIVE_API_URL=https://testnet.sentry.lcd.injective.network" >> .env
   echo "INJECTIVE_MAINNET_API_URL=https://sentry.lcd.injective.network" >> .env
   echo "OPENAI_API_BASE_URL=https://api.chatanywhere.tech" >> .env
   ```

3. **使用统一启动工具**：
   ```bash
   # 交互式菜单启动（推荐）
   python3 quick_start.py
   
   # 一键启动全套服务
   python3 quick_start.py all --auto
   
   # 仅启动服务器
   python3 quick_start.py service --auto
   
   # 仅启动客户端
   python3 quick_start.py client
   
   # 仅启动监控
   python3 quick_start.py monitor --auto
   ```

### 方案二：分步安装

1. **安装依赖包**：
   ```bash
   pip3 install -r requirements.txt
   ```

2. **启动代理服务器**：
   ```bash
   python3 quick_start_service.py --start
   ```

3. **连接代理**：
   ```bash
   python3 quick_start_client.py --url http://localhost:5000
   ```

### 方案三：Docker 安装

1. **克隆仓库**：
   ```bash
   git clone https://github.com/InjectiveLabs/iAgent.git
   cd iAgent
   ```

2. **构建 Docker 镜像**：
   ```bash
   docker build -t injective-agent .
   ```

3. **运行容器**：
   ```bash
   docker run -d \
     -p 5000:5000 \
     -e OPENAI_API_KEY="<YOUR_OPENAI_API_KEY_GOES_HERE>" \
     --name injective-agent \
     injective-agent
   ```

4. **连接代理**：
   ```bash
   python3 quick_start_client.py --url http://localhost:5000
   ```

**停止容器**：
```bash
docker stop injective-agent
```

**重启容器**：
```bash
docker start injective-agent
```

### 方案四：Docker Compose 安装

1. **使用 Docker Compose**：
   ```bash
   # 编辑 compose.yaml 文件，设置您的 OPENAI_API_KEY
   docker compose up -d
   ```

2. **查看服务状态**：
   ```bash
   docker compose ps
   docker compose logs -f
   ```

## 快速开始

### 🚀 一键启动（推荐）

使用统一启动工具，这是最简单的方式：

```bash
# 进入项目目录
cd iAgent

# 交互式启动（推荐）
python3 quick_start.py
```

然后按照提示选择：
1. **all** - 一键启动全套服务（服务器+监控+客户端）
2. **service** - 仅启动服务器管理
3. **client** - 仅启动客户端交互
4. **monitor** - 仅启动监控管理

### 🔧 服务器管理

```bash
# 启动服务器
python3 quick_start_service.py --start

# 停止服务器
python3 quick_start_service.py --stop

# 检查服务器状态
python3 quick_start_service.py --status

# 检查环境和依赖
python3 quick_start_service.py --check
```

### 💬 客户端交互

```bash
# 启动客户端
python3 quick_start_client.py

# 指定服务器地址
python3 quick_start_client.py --url http://localhost:5000

# 启用调试模式
python3 quick_start_client.py --debug
```

### 📊 监控管理

```bash
# 启动监控
python3 quick_start_monitor.py

# 自动监控模式
python3 quick_start_monitor.py --auto

# 生成监控报告
python3 quick_start_monitor.py --report

# 指定服务器地址
python3 quick_start_monitor.py http://localhost:5000
```

## Python3 报错修改策略

### 常见问题及解决方案

#### 1. Python 命令问题
**问题**：`Command 'python' not found`
**解决方案**：
```bash
# 方案A：安装 python-is-python3
sudo apt update
sudo apt install python-is-python3

# 方案B：创建别名
echo "alias python=python3" >> ~/.bashrc
source ~/.bashrc
```

#### 2. 依赖版本冲突
**问题**：`RequestsDependencyWarning: urllib3 (2.5.0) or chardet (5.2.0) doesn't match a supported version!`
**解决方案**：
```bash
# 使用修复脚本
python3 fix_dependencies.py

# 或手动更新依赖
pip3 install -r requirements.txt --upgrade
```

#### 3. OpenAI API 密钥错误
**问题**：`No OpenAI API key found`
**解决方案**：
```bash
# 设置环境变量
export OPENAI_API_KEY="your_openai_api_key_here"

# 或创建 .env 文件
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

#### 4. 私钥格式错误
**问题**：`non-hexadecimal number found in fromhex() arg`
**解决方案**：
- 系统已自动处理无效私钥
- 提供有效的十六进制私钥或使用默认值进行一般聊天

#### 5. API Token 限制
**问题**：免费 API 的 token 限制
**解决方案**：
- 系统提示已优化，减少 token 使用
- 考虑升级到付费 API 计划

## API 端点说明

### 基础端点
| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | API 信息和端点列表 |
| `/ping` | GET | 健康检查 |
| `/chat` | POST | 聊天接口 |
| `/history` | GET | 获取聊天历史 |
| `/clear` | POST | 清除聊天历史 |

### 聊天请求示例
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about Injective Chain",
    "session_id": "my_session",
    "agent_id": "my_agent",
    "environment": "testnet"
  }'
```

## 环境配置

### .env 文件配置
```bash
# OpenAI 配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE_URL=https://api.chatanywhere.tech

# Injective 网络配置
NETWORK=testnet
INJECTIVE_API_URL=https://testnet.sentry.lcd.injective.network
INJECTIVE_MAINNET_API_URL=https://sentry.lcd.injective.network
```

### 网络配置对应关系
| 网络类型 | NETWORK 值 | API 请求地址 |
|---------|------------|-------------|
| 测试网 | `testnet` | `https://testnet.sentry.lcd.injective.network` |
| 主网 | `mainnet` | `https://sentry.lcd.injective.network` |

## AI 代理使用指南

本指南将帮助您开始使用 AI 代理，包括如何使用命令、切换网络和管理代理。

### 代理配置文件
新的代理可以保存和更新在 `agents_config.yaml` 文件中，结构如下：
```yaml
agent10:
  address: <YOUR_WALLET_ADDRESS>
  created_at: '2024-11-07'
  private_key: <YOUR_WALLET_PRIVATEKEY>
  network: <YOUR_DESIRED_NETWORK>
```

**注意**：确保您的 OpenAI API 项目有足够的积分，并且可以访问 `gpt-4o` 模型。

## 🔧 自动化工具使用指南

项目提供了完整的自动化工具集，涵盖测试、监控、部署等各个方面。

### 统一启动工具

#### 主要功能
```bash
python3 quick_start.py [模式] [选项]
```

**可用模式：**
- `all` - 🎯 一键启动全套服务 ⭐ [推荐]
- `service` - 🔧 服务器管理（环境检查、启动、测试）
- `client` - 💬 客户端交互（代理管理、聊天交互）
- `monitor` - 📊 监控管理（实时监控、报告生成）

**使用示例：**
```bash
# 交互式菜单（推荐）
python3 quick_start.py

# 一键启动全套服务
python3 quick_start.py all --auto

# 仅启动服务器
python3 quick_start.py service --auto

# 仅启动客户端
python3 quick_start.py client --debug

# 仅启动监控
python3 quick_start.py monitor --report
```

### 测试工具套件

#### 1. 基础 API 测试
```bash
python3 test_agent_api.py
```
- ✅ 测试所有 API 端点 (`/`, `/ping`, `/chat`, `/history`, `/clear`)
- ✅ 验证服务器连接性和响应时间
- ✅ 检查聊天功能和历史记录管理
- ✅ 验证错误处理机制

#### 2. 区块链功能测试
```bash
python3 test_blockchain_functions.py
```
- 🔗 测试区块链查询功能 (余额、订单、市场数据)
- 💱 测试交易相关功能 (下单、撤单、交易历史)
- 🏦 测试质押功能和授权管理
- 🔧 测试高级区块链功能

#### 3. 无私钥环境测试
```bash
python3 test_without_private_key.py
```
- 🔒 测试无私钥情况下的基础功能
- 📊 API 端点可用性测试
- ⚡ 性能和错误处理测试

#### 4. 真实私钥测试
```bash
python3 test_with_real_private_key.py
```
⚠️ **注意**：此测试需要真实私钥，请在测试网环境下谨慎使用

#### 5. 综合测试套件
```bash
python3 run_all_tests.py
```
- 🧪 运行所有测试模块
- 📊 生成综合测试报告
- 📈 统计成功率和性能指标

#### 6. 详细测试报告生成
```bash
python3 generate_test_report.py
```
- 📋 生成详细的 JSON 格式测试报告
- ⚡ 包含性能压力测试
- 🔍 错误处理和边界情况测试

### 监控工具

#### 统一监控工具
```bash
python3 quick_start_monitor.py
```
- 📈 实时性能监控和系统资源监控
- 🏥 服务器健康状态检查和诊断
- ⏱️ 响应时间统计和成功率分析
- 🔧 Injective进程监控和管理
- 📋 自动生成监控报告
- 🎯 交互式监控面板

```bash
# 自动监控模式
python3 quick_start_monitor.py --auto

# 生成监控报告
python3 quick_start_monitor.py --report

# 指定服务器地址
python3 quick_start_monitor.py http://localhost:5000
```

### 配置管理工具

#### 配置管理器
```bash
python3 config_manager.py
```
- ⚙️ 环境配置检查和验证
- 🔑 API 密钥管理
- 🤖 代理配置导入/导出
- 📂 配置文件自动生成

#### 服务器管理工具
```bash
python3 quick_start_service.py
```
- 🚀 一键服务器启动和环境检查
- 🧪 自动化测试套件执行
- 📊 依赖检查和自动安装
- 🎯 交互式服务管理菜单

### 故障排除工具

#### 脚本兼容性测试
```bash
python3 test_script_compatibility.py
```
- 🔍 测试所有脚本的兼容性
- 📊 生成详细的兼容性报告
- ⚠️ 识别潜在问题

#### 依赖修复工具
```bash
python3 fix_dependencies.py
```
- 🔧 自动修复依赖版本冲突
- 📦 重新安装正确版本的包
- ✅ 验证依赖安装状态

#### 服务器状态检查
```bash
python3 check_server_status.py
```
- 🔍 检查服务器运行状态
- 📊 测试所有API端点
- 💡 提供修复建议

## 命令概览

AI 代理支持多个命令，分为一般操作、网络配置和代理管理。

### 一般命令
| 命令 | 描述 |
|------|------|
| `quit` | 退出代理会话 |
| `clear` | 清除当前会话输出 |
| `help` | 显示帮助信息 |
| `history` | 显示会话中的命令历史 |
| `ping` | 检查代理状态 |
| `debug` | 切换调试模式 |
| `session` | 显示当前会话详情 |

### 网络命令
| 命令 | 描述 |
|------|------|
| `switch_network` | 在 `mainnet` 和 `testnet` 环境之间切换 |

### 代理管理命令
| 命令 | 描述 |
|------|------|
| `create_agent` | 创建新的 AI 代理 |
| `delete_agent` | 删除现有的 AI 代理 |
| `switch_agent` | 切换到不同的 AI 代理 |
| `list_agents` | 显示可用代理列表 |

## 📁 项目文件结构

```
iAgent/
├── 📁 app/                          # 应用程序模块
│   └── agent_manager.py             # 多代理管理系统
├── 📁 assets/                       # 资源文件
│   └── logo.png                     # 项目 logo
├── 📁 injective_functions/          # Injective 区块链功能模块
│   ├── 📁 account/                  # 账户管理功能
│   ├── 📁 auction/                  # 拍卖功能
│   ├── 📁 authz/                    # 授权管理
│   ├── 📁 bank/                     # 银行和转账功能
│   ├── 📁 exchange/                 # 交易所功能
│   │   ├── exchange.py              # 市场数据和订单查询
│   │   └── trader.py                # 交易执行功能
│   ├── 📁 staking/                  # 质押功能
│   ├── 📁 token_factory/            # 代币工厂
│   ├── 📁 utils/                    # 工具函数
│   │   ├── function_helper.py       # 函数映射和执行器
│   │   ├── helpers.py               # 通用工具函数
│   │   ├── indexer_requests.py      # 索引器请求处理
│   │   └── initializers.py          # 客户端初始化器
│   ├── base.py                      # 基础类定义
│   └── factory.py                   # 客户端工厂
├── 📄 quick_start.py                # 🚀 统一启动工具（主要入口）
├── 📄 agent_server.py               # 🔥 核心服务器 (Quart 异步API)
├── 📄 quick_start_client.py         # 💬 CLI 客户端界面
├── 📄 quick_start_service.py        # 🔧 服务器管理工具
├── 📄 quick_start_monitor.py        # 📊 统一监控工具
├── 📄 config_manager.py             # ⚙️ 配置和密钥管理
├── 📄 auto_deploy.py                # 🤖 自动化部署工具
├── 📄 run_all_tests.py              # 🧪 测试套件执行器
├── 📄 generate_test_report.py       # 📋 测试报告生成器
├── 📄 test_agent_api.py             # ✅ API 端点测试
├── 📄 test_blockchain_functions.py  # 🔗 区块链功能测试
├── 📄 test_without_private_key.py   # 🔒 无私钥环境测试
├── 📄 test_with_real_private_key.py # 🔑 真实私钥测试
├── 📄 test_script_compatibility.py  # 🔍 脚本兼容性测试
├── 📄 fix_dependencies.py           # 🔧 依赖修复工具
├── 📄 check_server_status.py        # 🔍 服务器状态检查
├── 📄 agents_config.yaml            # 🤖 代理配置文件
├── 📄 agent_config.json             # ⚙️ 代理配置 (JSON格式)
├── 📄 requirements.txt              # 📦 Python 依赖
├── 📄 Dockerfile                    # 🐳 Docker 镜像构建
├── 📄 compose.yaml                  # 🐳 Docker Compose 配置
├── 📄 .env                          # 🔐 环境变量文件
├── 📄 FINAL_REPORT.md               # 📊 项目完成报告
├── 📄 AUTOMATION_README.md          # 🔧 自动化工具说明
├── 📄 ERROR_FIXES_SUMMARY.md        # 🔧 错误修复总结
├── 📄 SCRIPT_COMPATIBILITY_REPORT.md # 📊 脚本兼容性报告
└── 📄 readme_cn.md                  # 📖 中文文档
```

## 🔧 故障排除

### 常见问题及解决方案

#### 1. 服务器启动问题
**问题**：服务器无法启动
**解决方案**：
```bash
# 检查端口占用
netstat -tulpn | grep :5000
lsof -i :5000

# 杀死占用进程
sudo kill -9 <PID>

# 使用不同端口启动
python3 agent_server.py --port 5001
```

#### 2. API 连接问题
**问题**：API 连接失败或超时
**解决方案**：
```bash
# 检查服务器状态
python3 check_server_status.py

# 测试 API 端点
curl -X GET http://localhost:5000/ping

# 检查网络连接
curl -X GET http://localhost:5000/
```

#### 3. 私钥和配置问题
**问题**：私钥格式错误或配置无效
**解决方案**：
```bash
# 使用配置管理器验证
python3 config_manager.py

# 重新生成配置
rm agent_config.json agents_config.yaml
python3 auto_deploy.py
```

#### 4. 依赖版本冲突
**问题**：Python 包版本冲突
**解决方案**：
```bash
# 使用修复脚本
python3 fix_dependencies.py

# 或手动清理并重新安装
pip3 uninstall -y -r requirements.txt
pip3 install -r requirements.txt

# 使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### 调试和监控命令

#### 基础检查
```bash
# 检查服务器状态
curl http://localhost:5000/ping

# 查看所有 API 端点
curl http://localhost:5000/

# 测试聊天功能
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test"}'
```

#### 高级监控
```bash
# 统一监控工具
python3 quick_start_monitor.py

# 自动监控模式
python3 quick_start_monitor.py --auto

# 生成监控报告
python3 quick_start_monitor.py --report

# 运行完整测试套件
python3 run_all_tests.py

# 生成详细报告
python3 generate_test_report.py
```

#### 脚本兼容性检查
```bash
# 检查脚本兼容性
python3 test_script_compatibility.py

# 修复依赖问题
python3 fix_dependencies.py

# 检查服务器状态
python3 check_server_status.py
```

#### 日志和进程管理
```bash
# 检查 Python 进程
ps aux | grep python3
ps aux | grep agent_server

# 查看系统日志 (如果配置了日志文件)
tail -f /var/log/injective-agent.log

# 查看 Docker 日志 (如果使用 Docker)
docker logs injective-agent -f
```

## 📚 相关文档

### 重要文档文件
- 📄 `AUTOMATION_README.md` - 自动化工具详细说明
- 📊 `FINAL_REPORT.md` - 项目完成情况报告
- 🔧 `ERROR_FIXES_SUMMARY.md` - 错误修复总结
- 📊 `SCRIPT_COMPATIBILITY_REPORT.md` - 脚本兼容性报告
- 🧪 `all_tests_report.json` - 最新测试结果报告
- ⚙️ 各模块的 `*_schema.json` - API 功能定义文件

### 在线资源
- 🌐 [Injective Protocol 官方文档](https://docs.injective.network/)
- 🐍 [injective-py SDK 文档](https://github.com/InjectiveLabs/sdk-python)
- 🤖 [OpenAI API 文档](https://platform.openai.com/docs)

## 🤝 贡献指南

我们欢迎社区贡献！请遵循以下步骤：

1. **Fork 项目**：点击仓库页面的 Fork 按钮
2. **创建分支**：`git checkout -b feature/your-feature-name`
3. **提交修改**：`git commit -m "Add your feature"`
4. **推送分支**：`git push origin feature/your-feature-name`
5. **创建 Pull Request**：在 GitHub 上创建 PR

### 贡献类型
- 🐛 Bug 修复
- ✨ 新功能开发
- 📝 文档改进
- 🧪 测试用例添加
- 🔧 性能优化

## 🆘 获取帮助

### 社区支持
- 💬 [GitHub Issues](https://github.com/InjectiveLabs/iAgent/issues) - 报告问题和功能请求
- 📖 [GitHub Discussions](https://github.com/InjectiveLabs/iAgent/discussions) - 社区讨论
- 🌐 [Injective Discord](https://discord.gg/injective) - 实时交流

### 技术支持
如果遇到技术问题，请按以下顺序尝试：
1. 查看本文档的故障排除部分
2. 运行 `python3 test_script_compatibility.py` 检查脚本兼容性
3. 运行 `python3 fix_dependencies.py` 修复依赖问题
4. 运行 `python3 check_server_status.py` 检查服务器状态
5. 运行 `python3 generate_test_report.py` 生成诊断报告
6. 查看 `AUTOMATION_README.md` 中的详细说明
7. 在 GitHub Issues 中搜索相似问题
8. 创建新的 Issue 并附上诊断信息

## ⚠️ 免责声明

本仓库及其包含的信息（统称为"仓库"）仅用于信息和讨论目的，不构成也不应被解释为提供法律、财务、投资或商业建议。不保证本仓库中包含的任何信息或代码的准确性。

### 重要风险提示
- **私钥安全**：本项目涉及区块链私钥管理，请务必保护好您的私钥，避免在生产环境中使用测试私钥
- **资金安全**：建议先在测试网环境下充分测试，确认功能正常后再考虑在主网使用
- **API 安全**：请保护好您的 OpenAI API 密钥，避免在公开代码中暴露
- **交易风险**：数字资产交易具有高风险，可能导致资金损失
- **技术风险**：本软件处于开发阶段，可能存在未知漏洞

### 法律声明
数字资产的固有法律和监管风险不是本仓库的主题，不建议基于本仓库的内容做出购买、出售、交换或以其他方式使用任何数字资产的决定。**使用风险自负**。作者和所有关联方对您的交易结果不承担任何责任。

关于上述风险的可能性，应咨询适当的法律和/或监管顾问。应就所有与财务、商业、法律、监管和技术知识或专业知识相关的事项咨询自己的顾问。

使用、fork 或发布本仓库表示承认 Injective Labs Inc. 对任何其他相关方采取的行动相关的任何形式的责任都得到赔偿。用户或发布者明确承认该赔偿在法律上具有约束力，并且可以从本文档的所有其他部分中分离出来。

---

**最后更新时间**：2025年8月  
**版本**：v2.1.0 (根据脚本功能分析修正)  
**维护者**：Injective Labs 和开源社区
