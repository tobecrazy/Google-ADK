# Google ADK 旅行 AI 助手

一款基于 Google ADK（AI 开发工具包）构建的智能旅行规划助手，并通过 MCP（模型上下文协议）工具集成为实时数据访问提供增强功能。

## 🌟 功能特色

### 核心能力
- **🧠 智能旅行规划**: 生成包含景点、住宿、餐饮和交通的全面旅行行程
- **📅 智能日期解析**: 自动处理相对日期，如"后天"、"明天"、"3天后"
- **💰 预算优化**: 根据您的预算创建多个方案选项（经济型和高级版）
- **📊 可视化与 Markdown 报告**: 生成带有图片和信息的精美 HTML 和详细 Markdown 报告
- **🌐 实时数据**: 通过 MCP 工具访问当前天气、地图和位置数据。AttractionService 现在使用 Amap MCP 的实时数据。

### MCP 工具集成
- **⏰ 时间服务器**: 带及时区支持的精确日期/时间计算
- **🗺️ 高德地图**: 位置搜索、天气预报（独家来源）、实时景点数据和路线规划
- **🌐 网络获取**: 实时网络数据检索，用于餐厅页面和图像搜索
- **🧠 记忆服务器**: 用户偏好和旅行历史存储
- **🖼️ 图像服务**: 使用 MCP 获取增强的图像搜索和检索功能
- **🔄 异步加载**: 并行工具初始化以优化性能

## 🚀 快速开始

### 前置要求
- Python 3.8+
- Node.js（用于 MCP 服务器）
- ModelScope API Key（用于开源模型）
- 高德地图 API Key（可选，用于增强位置服务）

### 安装

1. **克隆仓库**
   ```bash
   git clone https://github.com/tobecrazy/Google-ADK.git
   cd Google-ADK
   ```

2. **设置 Python 环境**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # 在 Windows 上: .venv\\Scripts\\activate
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
   # 编辑 .env 文件并填入您的 API 密钥
   ```

### 环境配置

在 `travel_agent` 目录创建 `.env` 文件：

```env
# 必需: ModelScope API Key 用于开源模型
MODELSCOPE_API_KEY=your_modelscope_api_key_here

# 可选: 高德地图 API Key 用于增强位置服务
AMAP_MAPS_API_KEY=your_amap_api_key_here

# 可选: 其他服务 API 密钥
OPENWEATHER_API_KEY=your_openweather_key_here

# MCP 配置（防止超时问题）
MCP_TIMEOUT=30
MCP_RETRIES=3
MCP_LOG_LEVEL=info

# LiteLLM 配置
LITELLM_LOG=ERROR
LITELLM_MAX_RETRIES=3
LITELLM_TIMEOUT=30

# 旅行助手设置
DEFAULT_TIMEZONE=Asia/Shanghai
DEFAULT_CURRENCY=CNY
CACHE_ENABLED=true
CACHE_TTL=3600
```

### 模型更新

旅行助手现在使用 ModelScope 开源模型以增强性能和故障转移选项。模型配置为在遇到速率限制时自动切换，确保连续运行。这代表了从 Google 的 Gemini 模型到中国开源替代方案（包括 Qwen 和 DeepSeek 模型）的重大升级。

### 使用说明

确保在 `.env` 文件中正确设置了所有环境变量。助手现在支持高级模型配置和 MCP 工具集成以进行实时数据访问。

## 🛠️ 使用方法

### 基础使用

```python
from travel_agent.agent import create_robust_travel_agent

# 创建旅行助手
agent, status = create_robust_travel_agent()

# 检查 MCP 工具状态
print(f"可用 MCP 工具: {status.get('successful_tools', [])}")
print(f"工具总数: {status.get('registry_status', {}).get('total_tools', 0)}")

# 助手已准备好与 Google ADK 一起使用
```

### 使用异步的高级用法

```python
import asyncio
from travel_agent.agent import create_travel_agent_async

async def main():
    # 异步创建助手以获得更好性能
    agent, status = await create_travel_agent_async()
    
    # 检查详细状态
    if not status.get('fallback_mode'):
        registry_status = status.get('registry_status', {})
        print(f"MCP 工具按服务器分类:")
        for server, count in registry_status.get('tools_by_server', {}).items():
            print(f"  - {server}: {count} 个工具")

asyncio.run(main())
```

### 测试 MCP 集成

```bash
cd travel_agent
python test_mcp_simple.py
```

预期输出:
```
🚀 开始简单 MCP 测试
==================================================
📋 测试 1: 配置加载
找到 3 个基础配置:
  - 时间服务器 (必需)
  - 获取服务器 (可选)
  - 记忆服务器 (可选)
  - 高德地图服务器 (可选, 找到 API 密钥)

🔧 测试 2: 异步工具初始化
初始化结果:
  - 成功: ['时间服务器', '获取服务器', '记忆服务器', '高德地图服务器']
  - 失败: []
  - 成功率: 100.00%

📋 测试 3: 工具注册
注册状态:
  - 工具总数: 14
  - 按服务器分类: {'时间服务器': 2, '获取服务器': 1, '记忆服务器': 3, '高德地图服务器': 8}

🎉 核心功能测试通过!
```

## 🏗️ 架构

### MCP 工具集成架构

```
┌─────────────────────────────────────────────────────────────┐
│                    旅行 AI 助手                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ TravelAgent     │  │ DataCollector   │  │ ReportGen   │  │
│  │ Builder         │  │ Agent           │  │ Agent       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                   MCP 工具注册                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 异步工具初始化与管理                                      │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
│  │ 时间服务器   │ │ 高德地图     │ │ 网络获取     │ │ 记忆   │ │
│  │ (uvx)       │ │ (npm)       │ │ (uvx)       │ │ (npm)  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件

1. **MCPToolConfig**: 集中配置管理
2. **AsyncMCPToolInitializer**: 并行工具初始化与错误处理
3. **MCPToolRegistry**: 统一工具注册和异步调用
4. **TravelAgentBuilder**: 与 MCP 集成的清晰助手构建

## 📋 可用 MCP 工具

### 时间服务器（必需）
- `get_current_time`: 获取指定时区的当前时间
- `convert_time`: 在时区间转换时间

### 高德地图服务器（可选）
- `maps_weather`: 目的地天气预报
- `maps_text_search`: 搜索兴趣点
- `maps_around_search`: 查找附近位置
- `maps_geo`: 地理编码（地址到坐标）
- `maps_regeocode`: 逆地理编码（坐标到地址）
- `maps_direction_driving`: 驾车路线
- `maps_direction_walking`: 步行路线
- `maps_search_detail`: 详细 POI 信息

### 网络获取服务器（可选）
- `fetch`: 检索和处理网页内容、餐厅页面和图像搜索

### 记忆服务器（可选）
- `create_entities`: 存储旅行偏好
- `search_nodes`: 搜索存储的信息
- `open_nodes`: 检索特定数据

## 🔧 配置

### MCP 服务器配置

系统根据可用依赖项和 API 密钥自动配置 MCP 服务器：

```python
# 基础配置（总是尝试）
- 时间服务器: uvx mcp-server-time --local-timezone=Asia/Shanghai
- 获取服务器: uvx mcp-server-fetch  
- 记忆服务器: npx -y @modelcontextprotocol/server-memory

# 条件配置（基于 API 密钥）
- 高德地图: npx -y @amap/amap-maps-mcp-server (需要 AMAP_MAPS_API_KEY)
```

### 故障转移行为

系统提供优雅降级：
- **必需工具失败**: 助手切换到备用模式
- **可选工具失败**: 助手继续使用可用工具
- **所有工具失败**: 助手仅使用 AI 生成内容

## 🧪 测试

### 运行所有测试
```bash
cd travel_agent
python test_mcp_simple.py
```

### 测试独立组件
```bash
# 测试配置加载
python -c "from agent import MCPToolConfig; print(MCPToolConfig.get_base_configs())"

# 测试异步初始化
python -c "import asyncio; from agent import AsyncMCPToolInitializer; asyncio.run(AsyncMCPToolInitializer().initialize_all_tools_async())"
```

## 🚨 故障排除

### 常见问题

1. **MCP 服务器未找到**
   ```
   Command 'uvx' not found
   ```
   **解决方案**: 安装 uv: `pip install uv`

2. **高德 API 密钥问题**
   ```
   Amap Maps API key not found or invalid
   ```
   **解决方案**: 在 `.env` 文件中设置 `AMAP_MAPS_API_KEY`

3. **工具初始化超时**
   ```
   Tool initialization timeout
   ```
   **解决方案**: 检查网络连接并增加配置中的超时时间

4. **导入错误**
   ```
   No module named 'travel_agent'
   ```
   **解决方案**: 从正确目录运行并检查 Python 路径

### 调试模式

启用详细日志:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 最新更新

### v2.3.0 - 迁移到 ModelScope 开源模型
- ✅ **LLM 迁移**: 从 Google 的 Gemini 模型完全迁移到 ModelScope 开源模型 (Qwen, DeepSeek)
- ✅ **性能增强**: 提高响应速度并减少对外部 API 的依赖
- ✅ **国内模型支持**: 集成中国开源模型以获得更好的文化和语言背景
- ✅ **故障转移模型系统**: 在遇到速率限制时在模型之间自动切换 (Qwen, DeepSeek)
- ✅ **API 配置更新**: 从 GOOGLE_API_KEY 改为 MODELSCOPE_API_KEY 需求

### v2.2.0 - 增强网络获取和内容集成
- ✅ **MCP 获取服务集成**: 添加 `MCPFetchService` 和 `MCPImageService` 以增强内容和图像检索功能。
- ✅ **餐厅数据增强**: 更新 `restaurant_scraper.py` 以使用 MCP 服务获取餐厅页面和图像，并采用智能备用逻辑。
- ✅ **改进 URL 处理**: 增强 URL 处理和 DuckDuckGo 重定向解析，实现更可靠的网页内容获取。
- ✅ **图像搜索功能**: 使用 MCP 获取为餐厅、景点和食物提供新的图像搜索功能。
- ✅ **Python 发布工作流**: 为 Python 包发布添加自动化的 GitHub Actions 工作流。

### v2.1.0 - 实时数据和报告增强
- ✅ **实时景点数据**: `AttractionService` 现在使用 Amap MCP 检索实时景点信息，提供更准确和最新的推荐。
- ✅ **Markdown 报告生成**: 除了 HTML，助手现在生成详细 Markdown 格式的旅行报告。
- ✅ **简化的天气服务**: `WeatherService` 已重构为专门使用 Amap MCP 服务器获取所有天气数据，简化架构。
- ✅ **改进的成本显示**: HTML 旅行计划报告现在为预估成本提供增强的显示逻辑，提高用户清晰度。

### v2.0.0 - MCP 工具集成优化
- ✅ **异步工具加载**: MCP 服务器的并行初始化
- ✅ **清洁架构**: 分离关注点，使用专用类
- ✅ **错误处理**: 全面的错误处理和备用机制
- ✅ **工具注册**: 统一的工具管理和调用接口
- ✅ **配置管理**: 集中的 MCP 服务器配置
- ✅ **测试框架**: MCP 集成的全面测试套件
- ✅ **性能**: 工具初始化 100% 成功率
- ✅ **兼容性**: 与现有代码的向后兼容

### 主要改进
- **ModelScope 集成**: 从 Google 的 Gemini 完全迁移到中国开源模型 (Qwen, DeepSeek)
- **4+ MCP 服务器** 成功集成（时间、高德地图、网络获取、记忆、图像服务）
- **15+ 个工具** 可用于实时数据访问和内容检索
- **增强的网页抓取** 与 MCP 获取服务集成
- **智能图像搜索** 用于餐厅、景点和食物
- **异步/等待模式** 以实现最佳性能
- **工具不可用时的优雅降级**
- **用于调试和监控的详细状态报告**

## 🤝 贡献

1. Fork 仓库
2. 创建功能分支
3. 进行更改
4. 为新功能添加测试
5. 运行测试套件
6. 提交拉取请求

## 📄 许可证

本项目根据 MIT 许可证授权 - 详见 LICENSE 文件。

## 🙏 致谢

- Google ADK 团队提供 AI 开发框架
- ModelScope 团队提供开源大语言模型
- Model Context Protocol (MCP) 为工具集成标准
- 高德地图提供位置和天气服务
- 开源社区提供 MCP 服务器实现

---

**注意**: 本项目使用 Google ADK 和 MCP 的实验性功能。某些功能在未来版本中可能会有所变化。