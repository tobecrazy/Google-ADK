# 旅行规划AI Agent开发提示词

## 项目概述
开发一个基于Google ADK-Python的智能旅行规划AI Agent，能够根据用户输入的旅行信息自动生成详细的HTML格式旅行规划方案。

## 技术要求

### 1. 环境配置
- 使用Python 3.12+版本
- 创建虚拟环境：`python -m venv .venv`
- 激活虚拟环境后使用requirements.txt管理依赖
- 主要依赖包括：
  - google-generativeai
  - crawl4ai
  - requests
  - beautifulsoup4
  - jinja2
  - python-dateutil
  - aiohttp
  - asyncio
  - pytz（时区处理）
  - pillow（图片处理）

### 2. 核心功能模块设计

#### 输入参数处理模块
- 出发城市（必填）
- 旅行目的地（必填）
- 出发日期（默认：当前系统日期）
- 旅行天数（默认：1天）
- 预算金额（默认：100元人民币）

#### 信息采集模块（使用crawl4ai）
实现以下信息的自动抓取：
- 目的地基本信息（气候、文化、最佳旅行时间）
- 交通信息（往返交通工具、价格、时间）
- 住宿信息（酒店、民宿价格区间）
- 景点信息（门票价格、开放时间、推荐指数）
- 美食信息（特色餐厅、小吃、价格范围）
- 天气信息系统（详细天气预报与建议）

#### 天气信息集成模块
- 实时天气获取：当前天气状况、温度、湿度、风力等
- 未来天气预报：旅行期间逐日天气预报（最长支持15天）
- 沿途天气监控：主要景点和交通路线的天气状况
- 天气影响分析：根据天气条件调整景点推荐和行程安排
- 穿搭建议：基于天气和季节的着装推荐
- 活动适宜性：户外/室内活动的天气适宜度评估

#### 路线规划算法模块
- 基于预算约束的智能规划
- 考虑交通便利性的景点排序
- 时间优化的行程安排
- 餐饮费用合理分配

#### HTML生成模块
- 响应式设计，适配多种设备
- 图文并茂的展示效果
- 清晰的时间线布局
- 预算明细表格

## 详细实现要求

### 1. 数据抓取策略
使用crawl4ai实现以下网站信息抓取：
- 旅游网站（携程、去哪儿、马蜂窝）
- 交通信息（12306、航旅纵横）
- 住宿平台（美团、飞猪）
- 美食点评（大众点评、美团）
- 天气预报系统（中国天气网、天气通、AccuWeather）
- 沿途天气监控（高德地图天气、百度地图天气）

天气信息抓取重点：
- 目的地城市未来7-15天详细天气预报
- 主要景点实时天气状况
- 交通路线沿途天气变化
- 极端天气预警信息
- 空气质量指数（AQI）
- 紫外线指数和日出日落时间

抓取时需要：
- 设置合理的请求间隔，避免被封IP
- 使用User-Agent轮换
- 处理反爬虫机制
- 数据清洗和去重
- 天气数据实时更新机制

### 2. 智能规划算法
实现基于以下因素的综合评估：
- 预算约束（交通30%、住宿40%、餐饮20%、门票10%）
- 时间效率（最短路径、避开拥堵时段）
- 天气适应性（根据天气调整室内外活动比例）
- 用户偏好（根据历史数据学习）
- 季节性因素（淡旺季价格、天气影响）

天气智能决策系统：
- 雨天自动增加室内景点推荐权重
- 高温天气优先推荐有空调的场所
- 根据紫外线强度调整户外活动时间
- 空气质量差时推荐室内活动
- 极端天气预警时提供备选方案
- 基于天气的最佳出行时间建议

### 3. 多方案生成逻辑
生成至少两种不同类型的方案：
- 经济型方案：注重性价比，选择经济实惠的交通和住宿
- 舒适型方案：在预算内优先选择舒适度较高的选项
- 如预算充足，可增加豪华型方案

每个方案都包含天气适应性设计：
- 晴天方案：侧重户外景点和活动
- 雨天备选方案：重点推荐室内景点和体验
- 混合天气方案：灵活搭配室内外活动
- 极端天气应急方案：安全第一的室内替代方案

### 4. HTML模板设计要求
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{destination}}旅行规划</title>
    <style>
        /* 响应式CSS样式 */
        /* 支持深色/浅色主题切换 */
        /* 打印友好的样式 */
    </style>
</head>
<body>
    <!-- 页面结构应包含：
    1. 标题和基本信息摘要
    2. 预算分配饼图
    3. 天气概览卡片（含未来7天预报）
    4. 行程时间线（每日天气标识）
    5. 景点详情卡片（含图片和当日天气）
    6. 美食推荐区域
    7. 交通住宿信息
    8. 详细天气预报表格
    9. 天气相关的穿搭建议
    10. 紧急联系信息
    -->
</body>
</html>
```

### 5. 图片处理要求
- 自动获取景点高清图片
- 压缩图片以优化加载速度
- 添加图片alt属性提升可访问性
- 实现图片懒加载
- 提供图片加载失败的fallback

### 6. 内容质量控制
- 实现信息真实性验证机制
- 多源数据交叉验证
- 价格信息实时更新
- 内容去重和排重
- 字符编码统一处理（UTF-8）

## 代码结构建议

```
travel_agent/
├── agent.py                # Agent主程序入口
├── requirements.txt        # 依赖管理
├── config/
│   ├── settings.py        # 配置文件
│   └── prompts.py         # AI提示词模板
├── modules/
│   ├── input_handler.py   # 输入处理
│   ├── web_crawler.py     # 网络爬虫
│   ├── weather_service.py # 天气信息服务
│   ├── route_planner.py   # 路线规划
│   └── html_generator.py  # HTML生成
├── templates/
│   └── travel_plan.html   # HTML模板
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│       └── weather/       # 天气图标
└── utils/
    ├── data_cleaner.py    # 数据清洗
    ├── weather_analyzer.py # 天气分析工具
    └── validator.py       # 数据验证
```

## 错误处理和优化

### 1. 异常处理
- 网络请求超时处理
- 数据解析错误处理
- 预算不足的友好提示
- 无可用方案时的备选策略

### 2. 性能优化
- 使用异步编程提升爬取效率
- 实现缓存机制减少重复请求
- 数据库存储历史规划结果
- 并发处理多个信息源

### 3. 用户体验优化
- 进度条显示生成进度
- 实时预览功能
- 方案对比功能
- 一键导出PDF功能

## 测试要求
- 单元测试覆盖率达到80%以上
- 集成测试验证完整流程
- 性能测试确保响应时间<30秒
- 兼容性测试确保多平台运行

## 部署建议
- 支持Docker容器化部署
- 配置CI/CD自动化流程
- 实现日志监控和报警
- 支持水平扩展

## Agent入口文件设计要求

### agent.py 结构规范
```python
# agent.py - Agent Development Kit主程序入口
import asyncio
from typing import Dict, List, Optional
from google.generativeai import Agent
from modules.input_handler import InputHandler
from modules.web_crawler import WebCrawler
from modules.weather_service import WeatherService
from modules.route_planner import RoutePlanner
from modules.html_generator import HTMLGenerator

class TravelPlanningAgent(Agent):
    """旅行规划AI Agent主类"""
    
    def __init__(self):
        super().__init__()
        self.input_handler = InputHandler()
        self.web_crawler = WebCrawler()
        self.weather_service = WeatherService()
        self.route_planner = RoutePlanner()
        self.html_generator = HTMLGenerator()
    
    async def process_request(self, user_input: str) -> Dict:
        """处理用户旅行规划请求"""
        # Agent核心逻辑实现
        pass
    
    async def generate_travel_plans(self, travel_info: Dict) -> List[Dict]:
        """生成旅行规划方案"""
        # 多方案生成逻辑
        pass
    
    def run(self):
        """Agent运行入口"""
        # 启动Agent服务
        pass

if __name__ == "__main__":
    agent = TravelPlanningAgent()
    agent.run()
```

### Agent Development Kit集成要点
- 继承自google.generativeai.Agent基类
- 实现必要的Agent生命周期方法
- 支持异步处理和并发请求
- 集成Google ADK的工具和服务
- 实现Agent的状态管理和会话处理

## 使用示例
```python
# 创建并运行Agent实例
if __name__ == "__main__":
    # 启动Agent服务
    agent = TravelPlanningAgent()
    agent.run()

# 或者通过Agent Development Kit调用
from agent import TravelPlanningAgent

# 输入旅行信息
travel_info = {
    "departure_city": "北京",
    "destination": "三亚",
    "departure_date": "2025-08-01",
    "duration": 3,
    "budget": 3000
}

# 异步生成旅行规划（含天气信息）
agent = TravelPlanningAgent()
plans = await agent.generate_travel_plans(travel_info)

# 每个方案包含详细天气信息
for i, plan in enumerate(plans):
    print(f"方案 {i+1}:")
    print(f"- 天气概况: {plan.weather_summary}")
    print(f"- 穿搭建议: {plan.clothing_suggestions}")
    print(f"- 活动建议: {plan.activity_recommendations}")
    
    # 输出HTML格式的规划
    with open(f"travel_plan_{i+1}.html", "w", encoding="utf-8") as f:
        f.write(plan.to_html())
```

## 天气信息展示格式

### 1. 天气概览卡片
```html
<div class="weather-overview">
    <h3>旅行期间天气概况</h3>
    <div class="weather-summary">
        <div class="temp-range">温度范围: 25°C - 32°C</div>
        <div class="weather-trend">天气趋势: 多云转晴</div>
        <div class="rain-probability">降雨概率: 30%</div>
    </div>
</div>
```

### 2. 每日天气详情
```html
<div class="daily-weather">
    <div class="weather-day">
        <div class="date">8月1日</div>
        <div class="weather-icon">☀️</div>
        <div class="temperature">28°C / 22°C</div>
        <div class="conditions">晴天，微风</div>
        <div class="suggestions">适合户外活动</div>
    </div>
</div>
```

### 3. 景点天气标识
```html
<div class="attraction-weather">
    <span class="weather-badge sunny">☀️ 晴天</span>
    <span class="temp-badge">28°C</span>
    <span class="activity-badge">适合游览</span>
</div>
```

这个提示词涵盖了开发旅行规划AI Agent的所有关键要素，特别加强了天气信息的集成和展示，为用户提供更全面、实用的旅行规划服务。