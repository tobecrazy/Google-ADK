# 旅行规划AI Agent 开发提示词

## 项目概述
基于Google ADK-Python开发一个智能旅行规划AI Agent，能够根据用户输入的目的地、出发日期、旅行天数和预算，自动生成图文并茂的HTML格式旅行规划报告。具体代码实现可以参考：https://google.github.io/adk-docs/

## 环境配置提示词

### Python环境设置
```
请帮我创建一个Python 12+的开发环境：
1. 创建虚拟环境：python -m venv .venv
2. 激活虚拟环境并安装必要依赖
3. 配置Google ADK-Python开发环境
4. 设置.env文件用于存储API密钥
```

### 依赖包安装提示词
```
请为旅行规划AI Agent项目安装以下依赖包：
- requests（HTTP请求库）
- beautifulsoup4（网页解析）
- python-dotenv（环境变量管理）
- jinja2（HTML模板引擎）
- pillow（图片处理）
- datetime（日期时间处理）
- json（数据处理）
- logging（日志记录）
- pypinyin
- requests
- google-adk （Google ADK核心库）
- beautifulsoup4
- lxml
- google-generativeai
- google-cloud-aiplatform
- fastapi
- uvicorn
- python-dotenv
- httpx
- httpx-sse
- tenacity
- markdownify
- python-dateutil
- aiohttp
- asyncio
- pytz
- selenium
- webdriver_manager

```

## 核心功能开发提示词

### 1. 项目结构设计
```
请帮我设计一个清晰的项目目录结构：
├── main.py（主程序入口）
├── .env（环境变量配置文件）
├── requirements.txt（依赖包列表）
├── src/
│   ├── agents/
│      │
│      ├── .env
│      ├── travel_planner.py（旅行规划核心Agent）
│      ├── data_collector.py（数据收集Agent）
│      ├── report_generator.py（报告生成Agent）
│      ├── services/
│      │    ├── weather_service.py（天气API服务）
│      │    ├── attraction_service.py（景点信息服务）
│      │    ├── transport_service.py（交通信息服务）
│      │    └── accommodation_service.py（住宿信息服务）
│      ├── utils/
│      │    ├── web_scraper.py（网页爬虫工具）
│      │    ├── image_handler.py（图片处理工具）
│      │    └── budget_calculator.py（预算计算工具）
│      templates/
│           └── travel_plan.html（HTML模板）
│   
└── output/（生成的旅行规划文件）
```

### 2. 数据收集Agent提示词
```
请开发一个数据收集Agent，需要实现以下功能：

输入参数：
- departure_location: 出发地名称
- destination: 目的地名称
- start_date: 出发日期
- duration: 旅行天数
- budget: 预算金额

需要收集的数据：
1. 目的地基本信息（气候、最佳旅游时间、当地文化等）
2. 主要景点信息（门票价格、开放时间、推荐游览时长、图片、简介）
3. 交通信息（从出发地到目的地的交通方式、价格、时长）
4. 当地交通（公交、地铁、出租车价格）
5. 住宿信息（不同价位的酒店推荐、位置、价格区间）
6. 美食推荐（当地特色菜、餐厅推荐、价格区间、图片）
7. 天气预报（旅行期间的天气情况）

数据来源：
- 使用网络爬虫获取旅游网站信息
- 调用天气API获取天气预报
- 调用地图API获取地理位置和路线信息
- 调用图片搜索API获取景点和美食图片

注意事项：
- 确保数据的真实性和时效性
- 处理网络请求异常和数据解析错误
- 对获取的图片进行压缩和格式优化
- 实现数据缓存机制提高效率
```

### 3. 旅行规划核心Agent提示词
```
请开发旅行规划核心Agent，基于收集的数据生成智能旅行规划：

核心算法要求：
1. 根据预算自动筛选合适的景点、住宿和餐饮
2. 基于地理位置优化旅行路线，减少往返时间
3. 考虑景点开放时间和推荐游览时长安排行程
4. 平衡预算分配（交通30%、住宿35%、餐饮20%、门票15%）
5. 根据天气情况调整室内外活动安排

生成规划方案要求：
- 至少提供2种不同的规划方案（经济型和舒适型）
- 每个方案包含详细的日程安排（按小时安排）
- 提供备选景点和活动
- 计算详细的费用清单
- 给出实用的旅行建议和注意事项

输出格式要求：
- 结构化的数据格式（JSON）
- 包含所有必要的信息用于HTML生成
- 支持中英文输出
```

### 4. HTML报告生成Agent提示词
```
请开发HTML报告生成Agent，将旅行规划数据转换为图文并茂的HTML报告：

HTML模板设计要求：
1. 响应式设计，支持PC和移动端显示
2. 美观的UI界面，使用现代化的CSS样式
3. 清晰的信息层次结构
4. 图片轮播和缩放功能
5. 可打印的PDF格式支持

内容结构要求：
1. 旅行概况（目的地、日期、预算、天数）
2. 方案对比表格
3. 详细行程安排（每日安排）
4. 景点详情（图片、简介、门票、开放时间）
5. 美食推荐（图片、简介、价格、推荐餐厅）
6. 住宿推荐（图片、价格、位置、设施）
7. 交通安排（路线图、时间、费用）
8. 天气预报
9. 费用明细表
10. 实用信息和建议

技术实现要求：
- 使用Jinja2模板引擎
- 集成Bootstrap或类似CSS框架
- 图片懒加载和压缩
- 支持中文字符，防止乱码
- 生成的HTML文件可独立运行
```

### 5. Google ADK集成提示词
```
请将旅行规划AI Agent集成到Google ADK框架中：

ADK配置要求：
1. 创建ADK应用配置文件
2. 定义Agent的输入输出接口
3. 配置Web UI界面
4. 实现文件上传和下载功能
5. 添加进度条和状态提示
6. 支持多用户并发使用

Web界面要求：
1. 简洁直观的输入表单
2. 实时的处理进度显示
3. 方案预览和下载功能
4. 错误处理和用户提示
5. 响应式设计

部署要求：
- 支持本地开发环境运行
- 可部署到云平台
- 配置日志记录和监控
- 实现API接口供外部调用
```

## 详细任务拆分

### Phase 1: 环境准备与基础设置
**Task 1.1: 开发环境搭建**
```
1. 安装Python 12+
2. 创建虚拟环境：python -m venv .venv
3. 激活虚拟环境
4. 安装Google ADK-Python和相关依赖
5. 创建项目目录结构
6. 初始化Git仓库
```

**Task 1.2: 配置文件设置**
```
1. 使用已经存在的.env文件
2. 配置大模型API KEY（如OpenAI、Claude等）
3. 配置天气API KEY（如OpenWeatherMap）
4. 配置地图API KEY（如Google Maps）
5. 配置图片搜索API KEY
6. 设置项目基本配置参数
```

### Phase 2: 核心服务开发
**Task 2.1: 网络数据收集服务**
```
1. 开发web_scraper.py - 实现网页爬虫功能
   - 目标网站：携程、去哪儿、马蜂窝等旅游网站
   - 爬取景点信息、门票价格、开放时间
   - 爬取住宿信息、价格、评分
   - 实现反爬虫策略（User-Agent轮换、请求间隔）

2. 开发weather_service.py - 天气API服务
   - 集成OpenWeatherMap API
   - 获取目的地天气预报
   - 处理API异常和错误

3. 开发attraction_service.py - 景点信息服务
   - 整合多个数据源的景点信息
   - 数据清洗和标准化
   - 图片下载和处理

4. 开发transport_service.py - 交通信息服务
   - 查询火车、飞机、汽车票价
   - 当地交通费用计算
   - 路线规划和时间估算
```

**Task 2.2: 数据处理与存储**
```
1. 设计数据模型和存储结构
2. 实现数据缓存机制
3. 开发数据验证和清洗功能
4. 实现图片处理和优化功能
```

### Phase 3: AI Agent开发
**Task 3.1: 数据收集Agent**
```
1. 实现destination信息收集
2. 实现景点信息自动获取
3. 实现住宿信息收集
4. 实现美食信息收集
5. 实现交通信息收集
6. 集成天气预报功能
7. 实现数据质量检查
```

**Task 3.2: 旅行规划算法Agent**
```
1. 开发预算分配算法
   - 交通费用计算
   - 住宿费用计算
   - 餐饮费用估算
   - 门票费用统计

2. 开发路线优化算法
   - 基于地理位置的路线规划
   - 考虑交通时间和成本
   - 景点开放时间约束

3. 开发多方案生成算法
   - 经济型方案（预算优先）
   - 舒适型方案（体验优先）
   - 自定义权重调整

4. 实现行程时间安排算法
   - 按小时分配活动
   - 考虑休息时间
   - 预留弹性时间
```

**Task 3.3: 报告生成Agent**
```
1. 设计HTML模板结构
2. 开发模板渲染引擎
3. 实现图片展示功能
4. 开发响应式布局
5. 实现PDF导出功能
6. 添加交互式元素
```

### Phase 4: Google ADK集成
**Task 4.1: ADK应用配置**
```
1. 创建ADK应用配置文件
2. 定义Agent接口规范
3. 配置输入输出参数
4. 设置应用元数据
```

**Task 4.2: Web UI开发**
```
1. 设计用户输入界面
   - 目的地选择器
   - 日期选择器
   - 预算输入框
   - 旅行天数设置

2. 开发进度显示界面
   - 实时进度条
   - 处理状态提示
   - 错误信息显示

3. 实现结果展示界面
   - 方案对比视图
   - 详细规划展示
   - 下载功能按钮
```

**Task 4.3: 系统集成与测试**
```
1. 集成所有组件
2. 实现异常处理机制
3. 添加日志记录功能
4. 性能优化和调试
5. 用户体验测试
```

### Phase 5: 质量保证与部署
**Task 5.1: 测试与验证**
```
1. 单元测试开发
2. 集成测试执行
3. 用户接受测试
4. 性能压力测试
5. 数据质量验证
```

**Task 5.2: 文档与部署**
```
1. 编写用户使用文档
2. 编写开发者文档
3. 准备部署脚本
4. 配置监控和日志
5. 准备演示数据
```

## API配置说明

### .env文件配置模板
```bash
# 大模型API配置
OPENAI_API_KEY=your_openai_api_key
CLAUDE_API_KEY=your_claude_api_key

# 天气API配置
OPENWEATHER_API_KEY=your_openweather_api_key

# 地图API配置
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# 图片搜索API配置
UNSPLASH_API_KEY=your_unsplash_api_key

# 数据库配置（可选）
DATABASE_URL=sqlite:///travel_agent.db

# 应用配置
DEBUG=True
LOG_LEVEL=INFO
CACHE_TIMEOUT=3600
MAX_CONCURRENT_REQUESTS=10
```

## 质量控制要求

### 数据准确性保证
```
1. 多数据源交叉验证
2. 实时数据更新机制
3. 数据异常检测和处理
4. 用户反馈收集和改进
```

### 系统稳定性要求
```
1. 异常处理和错误恢复
2. 请求限流和超时处理
3. 内存和CPU使用优化
4. 并发处理能力
```

### 用户体验优化
```
1. 响应时间控制（<30秒生成规划）
2. 进度提示和状态反馈
3. 友好的错误提示
4. 多语言支持准备
```

## 项目里程碑

1. **Week 1-2**: 环境搭建和基础服务开发
2. **Week 3-4**: 核心AI Agent开发
3. **Week 5-6**: Google ADK集成和UI开发
4. **Week 7**: 测试和优化
5. **Week 8**: 文档和部署准备

## 成功标准

1. 能够根据用户输入自动生成2个不同的旅行规划方案
2. 生成的HTML报告图文并茂，排版美观
3. 预算计算准确，误差控制在10%以内
4. 系统响应时间控制在30秒以内
5. 支持至少10个主要旅游城市的规划
6. 在Google ADK平台上稳定运行
7. 用户满意度达到85%以上