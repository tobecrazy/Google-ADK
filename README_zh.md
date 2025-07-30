# Google ADK - AI智能旅行助手

一个全面的AI驱动旅行规划系统，利用Google Gemini AI和各种API创建个性化的旅行行程，集成实时数据并增强中文语言支持。

## 🌟 主要功能

### 核心能力
- **🤖 智能旅行规划**: 使用Google Gemini的AI驱动行程生成
- **🖼️ 真实景点图片**: 与Unsplash API集成，获取真实的景点照片
- **🚗 全面交通规划**: 详细的自驾、高铁和飞机出行规划
- **📅 智能日期解析**: 支持中文相对日期（"今天"、"明天"、"后天"）
- **🌤️ 实时天气**: 准确的天气预报，支持中文城市
- **💰 预算优化**: 智能预算分配（30%交通，35%住宿，20%餐饮，15%景点）
- **🌍 多语言支持**: 完整的中文语言处理和本地化
- **📱 响应式设计**: 适用于所有设备的精美HTML报告

### 高级功能
- **多代理架构**: 专门的数据收集、规划和报告生成代理
- **实时数据集成**: 实时天气、交通和住宿数据
- **动态网页抓取**: 智能数据收集与回退机制
- **交互式规划**: 对话式界面，用于迭代行程优化
- **导出功能**: 具有打印就绪格式的HTML报告

## 🏗️ 架构

系统采用模块化、多代理架构：

```
travel_agent/
├── main.py                     # 入口点和CLI界面
├── agent.py                    # 主协调代理
├── agents/                     # 专门的AI代理
│   ├── travel_planner.py       # 核心规划与日期解析
│   ├── data_collector.py       # 实时数据收集
│   └── report_generator.py     # HTML报告生成
├── services/                   # 外部API集成
│   ├── weather_service.py      # 增强天气服务（支持中文城市）
│   ├── attraction_service.py   # 真实景点数据解析
│   ├── transport_service.py    # 全面交通规划
│   ├── accommodation_service.py # 酒店和住宿
│   └── dialect_service.py      # 语言辅助
├── utils/                      # 辅助工具
│   ├── web_scraper.py          # 网页抓取（合规）
│   ├── image_handler.py        # 多源图片获取
│   ├── transport_crawler.py    # 实时交通数据
│   ├── budget_calculator.py    # 智能预算分配
│   ├── date_parser.py          # 中文日期处理
│   └── markdown_converter.py   # 内容格式化
├── templates/
│   └── travel_plan.html        # 增强的HTML模板
└── output/                     # 生成的旅行报告
```

## 🚀 快速开始

### 先决条件
- Python 3.9+
- Google API凭证（Gemini AI）
- 互联网连接以获取实时数据

### 安装

1. **克隆仓库**
   ```bash
   git clone https://github.com/tobecrazy/Google-ADK.git
   cd Google-ADK
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows上使用: .venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑.env文件，添加您的API密钥
   ```

### 必需的API密钥

将以下内容添加到您的`.env`文件中：

```env
# AI模型配置
GOOGLE_API_KEY=your_gemini_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE

# 天气服务（获取准确预报所必需）
OPENWEATHER_API_KEY=your_openweather_api_key

# 图片服务（可选 - 用于景点图片）
UNSPLASH_API_KEY=your_unsplash_api_key

# 网页抓取（可选）
FIRECRAWL_API_KEY=your_firecrawl_api_key

# 应用程序设置
DEBUG=True
LOG_LEVEL=INFO
```

### API密钥设置指南

1. **Google Gemini AI**（必需）
   - 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
   - 创建新的API密钥
   - 在`.env`中添加为`GOOGLE_API_KEY`

2. **OpenWeatherMap**（推荐）
   - 在[OpenWeatherMap](https://openweathermap.org/api)注册
   - 获取免费API密钥（每天1000次调用）
   - 在`.env`中添加为`OPENWEATHER_API_KEY`

3. **Unsplash**（可选 - 用于更好的图片）
   - 在[Unsplash Developers](https://unsplash.com/developers)注册
   - 创建应用程序并获取访问密钥
   - 在`.env`中添加为`UNSPLASH_API_KEY`

## 📖 使用方法

### 基本使用
```bash
cd travel_agent
python main.py
```

按照交互式提示输入：
- 目的地 (Destination): 例如 "东京" 或 "Tokyo"
- 出发地 (Departure): 例如 "上海" 或 "Shanghai"  
- 出发日期 (Start Date): 例如 "明天", "2024-03-15", "tomorrow"
- 旅行天数 (Duration): 例如 "5天" 或 "5 days"
- 预算 (Budget): 例如 "8000元" 或 "$1200"

### 编程使用
```python
from travel_agent.agent import TravelAgent

# 初始化代理
agent = TravelAgent()

# 使用中文输入规划旅行
trip_request = {
    "destination": "西安",
    "departure_location": "上海",
    "start_date": "明天",  # 智能日期解析
    "duration": "5天",
    "budget": "8000元"
}

# 生成全面的旅行计划
result = agent.plan_travel(**trip_request)
print(f"报告已生成: {result}")
```

### 高级示例

#### 商务旅行规划
```python
business_trip = agent.plan_travel(
    destination="Singapore",
    departure_location="Beijing",
    start_date="2024-04-01",
    duration="3 days",
    budget="$1500",
    trip_type="business"
)
```

#### 家庭度假
```python
family_trip = agent.plan_travel(
    destination="大连",
    departure_location="广州", 
    start_date="后天",  # 后天
    duration="7天",
    budget="15000元",
    travelers="2大人2小孩"
)
```

## 🎯 近期重大改进（2025年7月）

### ✅ 真实景点图片
- **问题**: HTML显示占位符渐变而非真实图片
- **解决方案**: 集成Unsplash API，使用智能搜索关键词
- **结果**: 每个景点现在都显示真实照片，并有优雅的回退机制

### ✅ 全面交通规划
- **问题**: 缺少详细的交通选择
- **解决方案**: 添加三种完整的交通模式：
  - **🚗 自驾**: 路线规划、燃油成本、过路费、停车估算
  - **🚄 高铁**: 时刻表、预订信息、座位类型、车站详情  
  - **✈️ 飞机**: 航班选项、机场、行李政策、时间建议
- **结果**: 每种选择的详细成本分析、优缺点和预订信息

### ✅ 智能日期解析
- **问题**: 不支持"今天"、"明天"、"后天"等相对日期
- **解决方案**: 集成实时系统日期与中文语言支持
- **结果**: 自然语言日期输入，自动验证

### ✅ 增强天气预报
- **问题**: 不准确的模拟天气数据
- **解决方案**: 集成OpenWeatherMap API，支持中文城市名称映射
- **结果**: 7天实时天气预报，带有季节性回退模式

### ✅ 完整中文本地化
- **问题**: 有限的中文语言处理能力
- **解决方案**: 增强拼音转换、文化背景和母语支持
- **结果**: 无缝的中文输入/输出，具有文化适宜性

## 🛠️ 开发

### 项目结构详情

#### 核心代理
- **TravelPlannerAgent**: 增强了智能日期解析和交通规划
- **DataCollectorAgent**: 实时数据收集与多源集成
- **ReportGeneratorAgent**: 精美的HTML生成与图片集成

#### 增强服务
- **WeatherService**: 多城市查询变体、季节性模式、中文城市映射
- **AttractionService**: 真实AI响应解析、图片集成、数据验证
- **TransportService**: 全面的交通选择与成本分析
- **ImageHandler**: 多源图片获取（Unsplash → Picsum → 占位符）

#### 智能工具
- **TransportCrawler**: 实时交通数据与智能回退
- **DateParser**: 中文相对日期处理与系统时间集成
- **BudgetCalculator**: 优化的分配算法
- **WebScraper**: 合规抓取与速率限制

### 测试

运行全面测试：
```bash
# 测试所有改进
python test_improvements.py

# 测试特定组件
python -m pytest tests/ -v

# 带覆盖率测试
python -m pytest tests/ --cov=travel_agent
```

### 添加新功能

1. **新服务集成**
   ```python
   # 在services/中创建服务
   class NewService:
       def __init__(self, api_key=None):
           self.api_key = api_key
       
       def get_data(self, query):
           # 实现带错误处理的代码
           pass
   ```

2. **扩展代理功能**
   ```python
   # 增强现有代理
   class EnhancedAgent(BaseAgent):
       def process_with_fallback(self, data):
           try:
               return self.primary_process(data)
           except Exception as e:
               return self.fallback_process(data)
   ```

## 📊 性能与质量

### 系统性能
- **响应时间**: 完整旅行计划15-30秒
- **图片加载**: 每个景点图片2-5秒
- **天气数据**: 实时API调用，1秒超时
- **内存使用**: 运行时约100-200MB
- **并发用户**: 支持多个同时请求

### 数据质量保证
- **多源验证**: 交叉引用多个API的数据
- **智能回退**: 服务不可用时的优雅降级
- **错误恢复**: 全面的异常处理
- **数据新鲜度**: 实时API集成与缓存优化性能

### 合规与道德
- **网页抓取**: 遵守robots.txt并实施速率限制
- **API使用**: 遵循所有服务条款和速率限制
- **数据隐私**: 不永久存储个人数据
- **准确性声明**: 清晰标注数据来源和限制

## 🎨 生成的报告

系统创建全面的HTML报告，包含以下内容：

### 📋 旅行概览
- 带文化洞察的目的地分析
- 智能解析的旅行日期与验证
- 详细的预算分解和分配
- 整个旅行期间的天气预报

### 🚗 交通分析（新增！）
- **三种详细选择**，包含完整成本分析
- **预订信息**和实用提示
- **优缺点比较**，便于决策
- **目的地当地交通**指南

### 🏛️ 景点体验（增强！）
- **来自Unsplash API的真实照片**
- **详细信息**: 开放时间、价格、游客提示
- **文化背景**和历史意义
- **基于兴趣和预算的智能推荐**

### 🏨 住宿与餐饮
- **带照片和位置地图的酒店推荐**
- **当地美食指南**，包含正宗餐厅照片
- **文化用餐提示**和礼仪指导
- **价格透明**，包含详细的成本分解

### 📊 智能行程
- **逐小时安排**，优化路线
- **多种场景**: 经济型vs舒适型选项
- **基于天气的调整**，安排室内外活动
- **实用旅行提示**和当地洞察

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 进行更改并进行适当测试
4. 使用清晰的消息提交 (`git commit -m 'Add amazing feature'`)
5. 推送到您的分支 (`git push origin feature/amazing-feature`)
6. 创建Pull Request，附上详细描述

### 开发指南
- 遵循PEP 8样式指南
- 添加全面的错误处理
- 为新功能编写单元测试
- 为API更改更新文档
- 使用中文和英文输入进行测试

## 🆘 故障排除

### 常见问题

**问题**: "No module named 'google.generativeai'"
**解决方案**: 安装Google AI SDK: `pip install google-generativeai`

**问题**: 天气数据显示"模拟数据"
**解决方案**: 在`.env`文件中添加有效的`OPENWEATHER_API_KEY`

**问题**: 报告中图片未加载
**解决方案**: 检查`UNSPLASH_API_KEY`或验证网络连接

**问题**: 中文输入日期解析错误
**解决方案**: 确保正确的UTF-8编码和系统区域设置

**问题**: 交通数据显示得很通用
**解决方案**: 系统在实时数据不可用时使用智能算法

### 获取帮助
- 查看 [Travel_AI_Agent.md](Travel_AI_Agent.md) 获取详细要求
- 查看现有的GitHub问题
- 创建新问题，附上详细的错误信息和重现步骤

## 📈 路线图

### 短期（1-3个月）
- [ ] 与官方预订API集成（12306、携程）
- [ ] 带Redis的高级缓存系统
- [ ] 移动响应式UI改进
- [ ] 多语言UI支持（英语、日语）

### 中期（3-6个月）
- [ ] 用于个性化推荐的机器学习
- [ ] 实时价格跟踪和警报
- [ ] 协作式旅行规划功能
- [ ] 高级分析和用户洞察

### 长期（6-12个月）
- [ ] 移动应用开发
- [ ] 企业功能和API市场
- [ ] 带偏好学习的高级AI
- [ ] 全球目的地扩展

## 📝 许可证

本项目采用MIT许可证 - 详情请见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- Google ADK团队提供的优秀开发框架
- OpenWeatherMap提供的可靠天气数据
- Unsplash提供的美丽目的地摄影
- 开源社区提供的宝贵工具和库

---

**用 ❤️ 制作，为智能旅行规划**

有关详细的开发文档，请参见 [Travel_AI_Agent.md](Travel_AI_Agent.md) | 有关技术改进，请参见 [COMPREHENSIVE_IMPROVEMENTS_SUMMARY.md](COMPREHENSIVE_IMPROVEMENTS_SUMMARY.md)