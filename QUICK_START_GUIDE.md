# 🚀 快速启动指南 - Injective Agent API

欢迎使用重新设计的 Injective Agent API 工具套件！我们已经将工具重新组织为三个专门的组件，每个都有明确的功能和用途。

## 📋 工具概览

| 工具 | 原名称 | 主要功能 | 使用场景 |
|------|--------|----------|----------|
| `quick_start_service.py` | `quick_start.py` | 🔧 服务器管理 | 部署、测试、环境管理 |
| `quick_start_client.py` | `quickstart.py` | 💬 CLI客户端 | 交易操作、代理管理 |
| `quick_start_monitor.py` | 新工具 | 📊 统一监控 | 性能监控、健康检查 |

## 🎯 典型使用流程

### 步骤 1: 环境部署和服务启动

```bash
# 方式一：一键自动部署
python3 quick_start_service.py --auto

# 方式二：交互式管理
python3 quick_start_service.py
```

**功能包括**：
- ✅ 自动检查和安装依赖
- ✅ 验证环境配置（.env文件、API密钥）
- ✅ 启动 agent_server.py
- ✅ 运行测试套件验证功能
- ✅ 启动监控服务

### 步骤 2: 系统监控和健康检查

```bash
# 方式一：实时监控面板
python3 quick_start_monitor.py --auto

# 方式二：生成监控报告
python3 quick_start_monitor.py --report

# 方式三：交互式监控菜单
python3 quick_start_monitor.py
```

**功能包括**：
- 📈 实时性能监控（CPU、内存、磁盘）
- 🏥 服务器健康状态检查
- ⏱️ API响应时间统计
- 🔧 Injective进程监控
- 📋 自动生成监控报告

### 步骤 3: 客户端交互和交易操作

```bash
# 连接到本地服务器
python3 quick_start_client.py --url http://localhost:5000

# 启用调试模式
python3 quick_start_client.py --debug
```

**功能包括**：
- 💬 自然语言交易指令
- 🤖 多代理创建和管理
- 🌐 网络切换（主网/测试网）
- 📊 交易结果格式化显示
- 🎨 美观的CLI界面

## 📖 详细使用示例

### 1. 首次部署流程

```bash
# 1. 克隆项目
git clone https://github.com/InjectiveLabs/iAgent.git
cd iAgent

# 2. 创建环境配置
echo "OPENAI_API_KEY=your_api_key_here" > .env
echo "NETWORK=testnet" >> .env

# 3. 一键部署和启动
python3 quick_start_service.py --auto

# 4. 在新终端启动监控
python3 quick_start_monitor.py --auto

# 5. 在第三个终端启动客户端
python3 quick_start_client.py
```

### 2. 日常使用工作流

```bash
# 每日启动检查
python3 quick_start_service.py --test     # 运行测试
python3 quick_start_monitor.py --report   # 生成健康报告

# 开始交易
python3 quick_start_client.py

# 在客户端中创建代理
create_agent trader1
switch_agent trader1

# 执行交易命令
查询我的余额
在INJ/USDT市场下一个买单
```

### 3. 故障排除流程

```bash
# 1. 检查服务器状态
python3 quick_start_monitor.py --report

# 2. 重启服务器
python3 quick_start_service.py --auto

# 3. 验证功能
python3 quick_start_service.py --test

# 4. 重新连接客户端
python3 quick_start_client.py
```

## 🔧 高级配置

### 服务器管理工具配置

```bash
# 自定义测试
python3 quick_start_service.py --test

# 启动监控模式
python3 quick_start_service.py --monitor

# 交互式菜单
python3 quick_start_service.py
```

### 监控工具配置

```bash
# 指定监控地址
python3 quick_start_monitor.py http://remote-server:5000

# 自动监控模式（后台运行）
nohup python3 quick_start_monitor.py --auto &

# 定时生成报告
while true; do python3 quick_start_monitor.py --report; sleep 3600; done
```

### 客户端配置

```bash
# 连接远程服务器
python3 quick_start_client.py --url http://remote-server:5000

# 启用调试模式
python3 quick_start_client.py --debug --url http://localhost:5000
```

## 🎨 工具特色功能

### quick_start_service.py 特色
- 🚀 **一键部署**: 自动检查环境、安装依赖、启动服务
- 🧪 **智能测试**: 运行完整测试套件并报告结果
- 📊 **状态监控**: 实时显示服务器和系统状态
- 🎯 **交互菜单**: 直观的操作选择界面

### quick_start_monitor.py 特色
- 📈 **实时面板**: 动态更新的监控面板
- 🏥 **健康检查**: 多端点健康状态检测
- 📋 **自动报告**: JSON格式的详细监控报告
- 🔧 **进程监控**: 专门监控Injective相关进程

### quick_start_client.py 特色
- 💬 **自然交互**: 支持自然语言交易指令
- 🎨 **美观界面**: 彩色终端和动画效果
- 🤖 **代理管理**: 完整的多代理生命周期管理
- 📊 **智能格式化**: 交易结果和余额的智能显示

## 🔗 工具间协作

这三个工具设计为协同工作：

1. **quick_start_service.py** 负责基础设施
2. **quick_start_monitor.py** 负责系统观测
3. **quick_start_client.py** 负责业务操作

它们可以独立运行，也可以组合使用，为不同的使用场景提供最佳体验。

## 📞 获取帮助

如果遇到问题，请按以下顺序尝试：

1. 运行 `python3 quick_start_monitor.py --report` 生成诊断报告
2. 查看生成的监控报告文件
3. 运行 `python3 quick_start_service.py --test` 验证系统
4. 查看 README 文档的故障排除部分
5. 在 GitHub Issues 中报告问题

---

**🎉 享受使用 Injective Agent API 工具套件！**
