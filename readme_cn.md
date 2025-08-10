![Banner!](assets/logo.png)
# Injective Agent 中文文档

欢迎使用基于OpenAI技术的Injective链交易代理系统。本系统专为Injective链设计，通过自然语言交互帮助您进行数据驱动的交易决策，包括数据分析、趋势预测和自动化交易执行。

## 系统概述

本项目利用OpenAI技术为Injective链提供以用户为中心的交易体验。代理系统能够理解自然语言指令，让您轻松管理各种交易任务。无论是市场监控、趋势预测还是交易执行，代理系统都能为您的战略决策提供支持。

## 核心特性

* **实时数据分析**: 获取即时市场洞察
* **预测分析**: 利用机器学习进行准确预测
* **自动化交易执行**: 在Injective链上无延迟执行交易决策
* **自然语言指令**: 使用日常语言指导代理行为
* **灵活配置**: 根据各种交易场景定制设置
* **简单部署**: 最小依赖，快速启动

## 系统要求

所有必需的包都列在requirements.txt中。确保您已安装Python 3.12+，然后按照安装部分安装依赖项。

## 系统组织架构

### 整体架构设计
```
iAgent/
├── app/                    # 应用核心模块
│   └── agent_manager.py   # 代理管理器
├── network/               # 网络连接模块
│   └── connectivity.py    # 连接性检查和注册
├── injective_functions/   # Injective链功能模块
│   ├── account/          # 账户管理
│   ├── auction/          # 拍卖功能
│   ├── authz/            # 授权管理
│   ├── bank/             # 银行功能
│   ├── exchange/         # 交易所功能
│   ├── staking/          # 质押功能
│   ├── token_factory/    # 代币工厂
│   └── utils/            # 工具函数
├── agent_server.py        # 主服务器
├── quick_start.py         # 统一启动工具
├── config_manager.py      # 配置管理器
└── requirements.txt       # 依赖包列表
```

### 核心模块说明

#### 1. 代理服务器 (agent_server.py)
- **InjectiveChatAgent类**: 核心AI代理类，集成OpenAI API
- **多API支持**: 支持OpenAI、DeepSeek、ChatAnywhere等API
- **函数执行器**: 集成Injective链功能函数
- **会话管理**: 支持多用户会话和对话历史
- **RESTful API**: 提供完整的HTTP接口

#### 2. 网络连接模块 (network/connectivity.py)
- **连接性检查**: 实时监控Injective网络状态
- **网络注册**: 管理主网和测试网连接
- **状态监控**: 提供网络健康状态报告

#### 3. 配置管理 (config_manager.py)
- **环境配置**: 管理API密钥和环境变量
- **代理配置**: 创建、更新、删除代理配置
- **区块链客户端**: 初始化和管理区块链连接
- **安全设置**: 配置速率限制、CORS等安全选项

#### 4. 统一启动工具 (quick_start.py)
- **多模式支持**: service、client、monitor、all四种模式
- **自动化部署**: 一键启动全套服务
- **进程管理**: 统一管理所有相关进程
- **交互式菜单**: 用户友好的操作界面

## 功能模块实现

### AI代理功能
- **自然语言理解**: 支持中文和英文指令
- **智能对话**: 基于上下文的连续对话
- **函数调用**: 自动识别和执行Injective链功能
- **多模型支持**: 支持GPT-4、DeepSeek等模型

### 区块链功能
- **账户管理**: 创建、导入、管理钱包账户
- **交易执行**: 支持现货交易、衍生品交易
- **质押管理**: 代币质押和奖励管理
- **代币操作**: 代币铸造、转账、销毁
- **拍卖参与**: 参与各种拍卖活动

### 安全功能
- **私钥管理**: 安全的私钥存储和验证
- **权限控制**: 基于角色的访问控制
- **交易验证**: 智能合约调用验证
- **审计日志**: 完整的操作记录

## 脚本启动模块汇总

### 主要启动脚本

#### 1. 统一启动工具 (quick_start.py)
```bash
# 交互式启动（推荐）
python3 quick_start.py

# 一键启动全套服务
python3 quick_start.py all --auto

# 仅启动服务器
python3 quick_start.py service --auto

# 仅启动客户端
python3 quick_start.py client --url http://localhost:5000

# 仅启动监控
python3 quick_start.py monitor --auto
```

#### 2. 服务器启动 (agent_server.py)
```bash
# 启动后端服务器（默认端口5000）
python agent_server.py --port 5000

# 指定端口启动
python agent_server.py --port 8080
```

#### 3. 客户端启动 (quick_start_client.py)
```bash
# 连接到指定服务器
python quick_start_client.py --url http://localhost:5000

# 调试模式
python quick_start_client.py --debug --url http://localhost:5000
```

#### 4. 服务管理 (quick_start_service.py)
```bash
# 启动服务
python quick_start_service.py --start

# 停止服务
python quick_start_service.py --stop

# 检查状态
python quick_start_service.py --status
```

### 启动模式详解

#### Service模式 - 服务器管理
- **环境检查**: 验证Python版本、依赖包、API密钥
- **自动部署**: 一键部署和配置服务器
- **服务控制**: 启动、停止、重启、状态检查
- **测试套件**: 运行完整的系统测试

#### Client模式 - 客户端交互
- **代理管理**: 创建、切换、删除AI代理
- **聊天交互**: 与AI代理进行自然语言对话
- **网络切换**: 在主网和测试网之间切换
- **调试支持**: 详细的调试信息和日志

#### Monitor模式 - 监控管理
- **实时监控**: 监控服务器状态和性能
- **网络监控**: 监控Injective网络连接性
- **报告生成**: 生成详细的监控报告
- **告警通知**: 异常状态告警

#### All模式 - 全套服务
- **一键启动**: 自动启动所有相关服务
- **进程管理**: 统一管理所有进程
- **后台运行**: 支持后台运行模式
- **自动恢复**: 服务异常自动重启

## 安装指南

### 方式一：本地安装

1. 克隆仓库并进入目录:
   ```bash
   git clone https://github.com/InjectiveLabs/iAgent.git
   cd iAgent  
   ```

2. 安装依赖包:
   ```bash  
   pip install -r requirements.txt  
   ```

3. 设置OpenAI API密钥:
   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"
   ```

4. 启动代理:
   ```bash
   # 启动后端服务器
   python agent_server.py --port 5000  
   
   # 连接到代理进行交互
   python quick_start.py --url http://0.0.0.0:5000
   ```

### 方式二：Docker安装

1. 克隆仓库:
   ```bash
   git clone https://github.com/InjectiveLabs/iAgent.git
   cd iAgent
   ```

2. 构建Docker镜像:
   ```bash
   docker build -t injective-agent .
   ```

3. 运行容器:
   ```bash
   docker run -d \
     -p 5000:5000 \
     -e OPENAI_API_KEY="<YOUR_OPENAI_API_KEY_GOES_HERE>" \
     --name injective-agent \
     injective-agent
   ```

4. 连接到代理:
   ```bash
   python quick_start.py --url http://localhost:5000
   ```

## AI代理使用指南

本指南将帮助您开始使用AI代理，包括如何使用命令、切换网络和管理代理。

新代理可以保存和更新在agents_config.yaml文件中，YAML文件结构如下：
```yaml
agent10:
  address: <YOUR_WALLET_ADDRESS>
  created_at: '2024-11-07'
  private_key: <YOUR_WALLET_PRIVATEKEY>
  network: <YOUR_DESIRED_NETWORK>
```

请确保您的OpenAI API项目有足够的积分，并且可以访问`gpt-4o`模型。

## 命令概览

AI代理支持多种命令，分为通用操作、网络配置和代理管理。

### 通用命令
| 命令      | 描述                                |
|-----------|--------------------------------------------|
| `quit`    | 退出代理会话                            |
| `clear`   | 清除当前会话输出                        |
| `help`    | 显示帮助信息                            |
| `history` | 显示会话中的命令历史                    |
| `ping`    | 检查代理状态                            |
| `debug`   | 切换调试模式                            |
| `session` | 显示当前会话详情                        |

### 网络命令
| 命令             | 描述                                        |
|------------------|----------------------------------------------------|
| `switch_network` | 在`mainnet`和`testnet`环境之间切换                |

### 代理管理命令
| 命令              | 描述                                   |
|-------------------|-----------------------------------------------|
| `create_agent`    | 创建新的AI代理                            |
| `delete_agent`    | 删除现有AI代理                            |
| `switch_agent`    | 切换到不同的AI代理                        |
| `list_agents`     | 显示可用代理列表                          |

## 配置说明

### 环境变量配置
```bash
# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE_URL=https://api.openai.com

# DeepSeek API配置（可选）
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_BASE_URL=https://api.deepseek.com

# 服务器配置
HOST=0.0.0.0
PORT=5000
DEBUG=false
```

### 代理配置文件
系统支持多种配置格式：
- `agent_config.json`: 主要配置文件
- `agents_config.yaml`: 代理配置文件
- `.env`: 环境变量文件

## 故障排除

### 常见问题

1. **API密钥错误**: 检查环境变量设置
2. **网络连接失败**: 验证Injective网络状态
3. **依赖包缺失**: 运行`pip install -r requirements.txt`
4. **端口占用**: 使用`--port`参数指定不同端口

### 日志文件
- `server.log`: 服务器运行日志
- `agent.log`: 代理操作日志

## 贡献指南

欢迎贡献！请fork仓库并提交pull request。

## 免责声明

本仓库及其包含的信息（统称为"仓库"）仅用于信息和讨论目的，不构成也不应被解释为提供法律、财务、投资或商业建议。对于此处包含的任何信息或代码的准确性，不提供任何保证或担保。数字资产的合法和监管风险不是本仓库的主题，基于本仓库内容不建议做出购买、出售、交换或以其他方式使用任何数字资产的决定。使用风险自负。作者和所有附属公司对您的交易结果不承担任何责任。关于上述风险可能性的指导，应咨询适当的法律和/或监管顾问。应咨询自己的顾问以了解与财务、商业、法律、监管和技术知识或专业知识相关的所有事项。使用、fork或发布本仓库表示承认Injective Labs Inc.不对任何其他相关方采取的行动承担任何形式的责任。用户或发布者明确承认该赔偿在法律上具有约束力，并且与本文档的所有其他部分可分离。
