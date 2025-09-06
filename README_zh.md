# Google ADK 旅游 AI 代理

一个基于 Google ADK (AI 开发套件) 构建的智能旅游规划助手，并集成了 MCP (模型上下文协议) 工具以实现实时数据访问。

## 🌟 功能

### 核心能力
- **🧠 智能旅游规划**: 生成包含景点、住宿、餐饮和交通的综合旅游行程。
- **📅 智能日期解析**: 自动处理相对日期，如“后天”、“明天”、“3天后”。
- **💰 预算优化**: 根据您的预算创建多种计划选项 (经济型和豪华型)。
- **📊 可视化和 Markdown 报告**: 生成精美的 HTML 和详细的 Markdown 报告，包含图片和信息。
- **🌐 实时数据**: 通过 MCP 工具访问当前天气、地图和位置数据。`AttractionService` 现在使用来自高德地图 MCP 的实时数据。

### MCP 工具集成
- **⏰ 时间服务器**: 支持时区的精确日期/时间计算。
- **🗺️ 高德地图**: 位置搜索、天气预报 (独家来源)、实时景点数据和路线规划。
- **🌐 网页抓取**: 实时网页数据检索。
- **🧠 记忆**: 存储用户偏好和旅行历史。
- **🔄 异步加载**: 并行工具初始化以获得最佳性能。

## 🚀 快速入门

### 先决条件
- Python 3.8+
- Node.js (用于 MCP 服务器)
- Google API 密钥 (用于 Gemini)
- 高德 API 密钥 (可选，用于增强定位服务)

### 安装

1. **克隆仓库**
   ```bash
   git clone https://github.com/tobecrazy/Google-ADK.git
   cd Google-ADK
   ```

2. **设置 Python 环境**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # 在 Windows 上: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **安装 MCP 依赖**
   ```bash
   # 为基于 Python 的 MCP 服务器安装 uvx
   pip install uv
   
   # 安装 Node.js MCP 服务器
   npm install -g @modelcontextprotocol/server-memory
   npm install -g @amap/amap-maps-mcp-server
   ```

4. **配置环境变量**
   ```bash
   cd travel_agent
   cp .env.example .env
   # 在 .env 文件中编辑您的 API 密钥
   ```

## 🔄 最近更新

### v2.1.0 - 实时数据和报告增强
- ✅ **实时景点数据**: `AttractionService` 现在使用高德地图 MCP 检索实时景点信息，提供更准确、更及时的推荐。
- ✅ **Markdown 报告生成**: 除了 HTML，代理现在还生成详细的 Markdown 格式的旅行报告。
- ✅ **简化的天气服务**: `WeatherService` 已重构为专门使用高德地图 MCP 服务器获取所有天气数据，简化了架构。
- ✅ **改进的费用显示**: HTML 旅行计划报告现在具有增强的预估费用显示逻辑，提高了用户的清晰度。

### v2.0.0 - MCP 工具集成优化
- ✅ **异步工具加载**: MCP 服务器的并行初始化。
- ✅ **清晰的架构**: 通过专用类分离关注点。
- ✅ **错误处理**: 全面的错误处理和回退机制。
- ✅ **工具注册表**: 统一的工具管理和调用接口。
- ✅ **配置管理**: 集中的 MCP 服务器配置。
- ✅ **测试框架**: 用于 MCP 集成的综合测试套件。
- ✅ **性能**: 工具初始化成功率 100%。
- ✅ **兼容性**: 与现有代码向后兼容。

### 主要改进
- **4 个 MCP 服务器** 成功集成 (时间、高德地图、网页抓取、记忆)。
- **14 个总工具** 可用于实时数据访问。
- **异步/等待模式** 以获得最佳性能。
- **优雅降级** 当工具不可用时。
- **详细的状态报告** 用于调试和监控。

## 🤝 贡献

1. Fork 仓库
2. 创建功能分支
3. 进行更改
4.为新功能添加测试
5. 运行测试套件
6. 提交拉取请求

## 📄 许可证

该项目根据 MIT 许可证授权 - 有关详细信息，请参阅 LICENSE 文件。
