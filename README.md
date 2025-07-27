# Google ADK - AI-Powered Travel Agent

A comprehensive AI-powered travel planning system that leverages Google's Gemini AI and various APIs to create personalized travel itineraries with real-time data integration and enhanced Chinese language support.

## 🌟 Key Features

### Core Capabilities
- **🤖 Intelligent Travel Planning**: AI-powered itinerary generation using Google Gemini
- **🖼️ Real Attraction Images**: Integration with Unsplash API for authentic destination photos
- **🚗 Comprehensive Transportation**: Detailed planning for 自驾 (driving), 高铁 (high-speed rail), and 飞机 (flights)
- **📅 Smart Date Parsing**: Support for Chinese relative dates ("今天", "明天", "后天")
- **🌤️ Real-time Weather**: Accurate weather forecasts with Chinese city support
- **💰 Budget Optimization**: Intelligent budget allocation (30% transport, 35% accommodation, 20% dining, 15% attractions)
- **🌍 Multi-language Support**: Full Chinese language processing and localization
- **📱 Responsive Design**: Beautiful HTML reports optimized for all devices

### Advanced Features
- **Multi-Agent Architecture**: Specialized agents for data collection, planning, and report generation
- **Real-time Data Integration**: Live weather, transportation, and accommodation data
- **Dynamic Web Scraping**: Intelligent data collection with fallback mechanisms
- **Interactive Planning**: Conversational interface for iterative trip refinement
- **Export Capabilities**: HTML reports with print-ready formatting

## 🏗️ Architecture

The system uses a modular, multi-agent architecture:

```
travel_agent/
├── main.py                     # Entry point and CLI interface
├── agent.py                    # Main orchestrator agent
├── agents/                     # Specialized AI agents
│   ├── travel_planner.py       # Core planning with date parsing
│   ├── data_collector.py       # Real-time data gathering
│   └── report_generator.py     # HTML report generation
├── services/                   # External API integrations
│   ├── weather_service.py      # Enhanced weather with Chinese cities
│   ├── attraction_service.py   # Real attraction data parsing
│   ├── transport_service.py    # Comprehensive transportation
│   ├── accommodation_service.py # Hotel and lodging
│   └── dialect_service.py      # Language assistance
├── utils/                      # Helper utilities
│   ├── web_scraper.py          # Web scraping with compliance
│   ├── image_handler.py        # Multi-source image fetching
│   ├── transport_crawler.py    # Real-time transport data
│   ├── budget_calculator.py    # Smart budget allocation
│   ├── date_parser.py          # Chinese date processing
│   └── markdown_converter.py   # Content formatting
├── templates/
│   └── travel_plan.html        # Enhanced HTML template
└── output/                     # Generated travel reports
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Google API credentials (Gemini AI)
- Internet connection for real-time data

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tobecrazy/Google-ADK.git
   cd Google-ADK
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

### Required API Keys

Add these to your `.env` file:

```env
# AI Model Configuration
GOOGLE_API_KEY=your_gemini_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE

# Weather Service (Required for accurate forecasts)
OPENWEATHER_API_KEY=your_openweather_api_key

# Image Service (Optional - for attraction images)
UNSPLASH_API_KEY=your_unsplash_api_key

# Web Scraping (Optional)
FIRECRAWL_API_KEY=your_firecrawl_api_key

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
```

### API Keys Setup Guide

1. **Google Gemini AI** (Required)
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add to `.env` as `GOOGLE_API_KEY`

2. **OpenWeatherMap** (Recommended)
   - Register at [OpenWeatherMap](https://openweathermap.org/api)
   - Get free API key (1000 calls/day)
   - Add to `.env` as `OPENWEATHER_API_KEY`

3. **Unsplash** (Optional - for better images)
   - Register at [Unsplash Developers](https://unsplash.com/developers)
   - Create application and get access key
   - Add to `.env` as `UNSPLASH_API_KEY`

## 📖 Usage

### Basic Usage
```bash
cd travel_agent
python main.py
```

Follow the interactive prompts to enter:
- 目的地 (Destination): e.g., "东京" or "Tokyo"
- 出发地 (Departure): e.g., "上海" or "Shanghai"  
- 出发日期 (Start Date): e.g., "明天", "2024-03-15", "tomorrow"
- 旅行天数 (Duration): e.g., "5天" or "5 days"
- 预算 (Budget): e.g., "8000元" or "$1200"

### Programmatic Usage
```python
from travel_agent.agent import TravelAgent

# Initialize the agent
agent = TravelAgent()

# Plan a trip with Chinese input
trip_request = {
    "destination": "京都",
    "departure_location": "上海",
    "start_date": "明天",  # Smart date parsing
    "duration": "5天",
    "budget": "8000元"
}

# Generate comprehensive travel plan
result = agent.plan_travel(**trip_request)
print(f"Report generated: {result}")
```

### Advanced Examples

#### Business Trip Planning
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

#### Family Vacation
```python
family_trip = agent.plan_travel(
    destination="大阪",
    departure_location="广州", 
    start_date="后天",  # Day after tomorrow
    duration="7天",
    budget="15000元",
    travelers="2大人2小孩"
)
```

## 🎯 Recent Major Improvements (2025-07)

### ✅ Real Attraction Images
- **Problem**: HTML showed placeholder gradients instead of real images
- **Solution**: Integrated Unsplash API with intelligent search keywords
- **Result**: Every attraction now displays authentic photos with elegant fallbacks

### ✅ Comprehensive Transportation Planning
- **Problem**: Missing detailed transportation options
- **Solution**: Added three complete transport modes:
  - **🚗 自驾 (Self-driving)**: Route planning, fuel costs, tolls, parking estimates
  - **🚄 高铁 (High-speed rail)**: Schedules, booking info, seat types, station details  
  - **✈️ 飞机 (Airplane)**: Flight options, airports, baggage policies, timing recommendations
- **Result**: Detailed cost analysis, pros/cons, and booking information for each option

### ✅ Smart Date Parsing
- **Problem**: No support for relative dates like "今天", "明天", "后天"
- **Solution**: Real-time system date integration with Chinese language support
- **Result**: Natural language date input with automatic validation

### ✅ Enhanced Weather Forecasts
- **Problem**: Inaccurate mock weather data
- **Solution**: OpenWeatherMap API integration with Chinese city name mapping
- **Result**: 7-day real weather forecasts with seasonal fallback patterns

### ✅ Full Chinese Localization
- **Problem**: Limited Chinese language processing
- **Solution**: Enhanced Pinyin conversion, cultural context, and native language support
- **Result**: Seamless Chinese input/output with cultural appropriateness

## 🛠️ Development

### Project Structure Details

#### Core Agents
- **TravelPlannerAgent**: Enhanced with smart date parsing and transportation planning
- **DataCollectorAgent**: Real-time data gathering with multiple source integration
- **ReportGeneratorAgent**: Beautiful HTML generation with image integration

#### Enhanced Services
- **WeatherService**: Multiple city query variations, seasonal patterns, Chinese city mapping
- **AttractionService**: Real AI response parsing, image integration, data validation
- **TransportService**: Comprehensive transport options with cost analysis
- **ImageHandler**: Multi-source image fetching (Unsplash → Picsum → Placeholders)

#### Smart Utilities
- **TransportCrawler**: Real-time transport data with intelligent fallbacks
- **DateParser**: Chinese relative date processing with system time integration
- **BudgetCalculator**: Optimized allocation algorithms
- **WebScraper**: Compliant scraping with rate limiting

### Testing

Run comprehensive tests:
```bash
# Test all improvements
python test_improvements.py

# Test specific components
python -m pytest tests/ -v

# Test with coverage
python -m pytest tests/ --cov=travel_agent
```

### Adding New Features

1. **New Service Integration**
   ```python
   # Create service in services/
   class NewService:
       def __init__(self, api_key=None):
           self.api_key = api_key
       
       def get_data(self, query):
           # Implementation with error handling
           pass
   ```

2. **Extend Agent Capabilities**
   ```python
   # Enhance existing agents
   class EnhancedAgent(BaseAgent):
       def process_with_fallback(self, data):
           try:
               return self.primary_process(data)
           except Exception as e:
               return self.fallback_process(data)
   ```

## 📊 Performance & Quality

### System Performance
- **Response Time**: 15-30 seconds for complete travel plans
- **Image Loading**: 2-5 seconds per attraction image
- **Weather Data**: Real-time API calls with 1-second timeout
- **Memory Usage**: ~100-200MB during operation
- **Concurrent Users**: Supports multiple simultaneous requests

### Data Quality Assurance
- **Multi-source Validation**: Cross-reference data from multiple APIs
- **Intelligent Fallbacks**: Graceful degradation when services unavailable
- **Error Recovery**: Comprehensive exception handling throughout
- **Data Freshness**: Real-time API integration with caching for performance

### Compliance & Ethics
- **Web Scraping**: Respects robots.txt and implements rate limiting
- **API Usage**: Follows all service terms and rate limits
- **Data Privacy**: No personal data stored permanently
- **Accuracy Disclaimer**: Clear labeling of data sources and limitations

## 🎨 Generated Reports

The system creates comprehensive HTML reports featuring:

### 📋 Travel Overview
- Destination analysis with cultural insights
- Smart-parsed travel dates with validation
- Detailed budget breakdown and allocation
- Weather forecast for entire trip duration

### 🚗 Transportation Analysis (NEW!)
- **Three detailed options** with complete cost analysis
- **Booking information** and practical tips
- **Pros & cons comparison** for informed decisions
- **Local transportation** guide for destination

### 🏛️ Attraction Experience (ENHANCED!)
- **Real photographs** from Unsplash API
- **Detailed information**: hours, prices, visitor tips
- **Cultural context** and historical significance
- **Smart recommendations** based on interests and budget

### 🏨 Accommodation & Dining
- **Hotel recommendations** with photos and location maps
- **Local cuisine guide** with authentic restaurant photos
- **Cultural dining tips** and etiquette guidance
- **Price transparency** with detailed cost breakdowns

### 📊 Smart Itinerary
- **Hour-by-hour scheduling** with optimized routing
- **Multiple scenarios**: Economic vs. Comfort options
- **Weather-based adjustments** for indoor/outdoor activities
- **Practical travel tips** and local insights

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with proper testing
4. Commit with clear messages (`git commit -m 'Add amazing feature'`)
5. Push to your branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request with detailed description

### Development Guidelines
- Follow PEP 8 style guidelines
- Add comprehensive error handling
- Include unit tests for new features
- Update documentation for API changes
- Test with both Chinese and English inputs

## 🆘 Troubleshooting

### Common Issues

**Issue**: "No module named 'google.generativeai'"
**Solution**: Install Google AI SDK: `pip install google-generativeai`

**Issue**: Weather data shows "Mock data"
**Solution**: Add valid `OPENWEATHER_API_KEY` to your `.env` file

**Issue**: Images not loading in reports
**Solution**: Check `UNSPLASH_API_KEY` or verify internet connection

**Issue**: Date parsing errors with Chinese input
**Solution**: Ensure proper UTF-8 encoding and system locale settings

**Issue**: Transportation data seems generic
**Solution**: The system uses intelligent algorithms when real-time data unavailable

### Getting Help
- Check the [Travel_AI_Agent.md](Travel_AI_Agent.md) for detailed requirements
- Review existing GitHub issues
- Create new issue with detailed error information and steps to reproduce

## 📈 Roadmap

### Short-term (1-3 months)
- [ ] Integration with official booking APIs (12306, Ctrip)
- [ ] Advanced caching system with Redis
- [ ] Mobile-responsive UI improvements
- [ ] Multi-language UI support (English, Japanese)

### Medium-term (3-6 months)
- [ ] Machine learning for personalized recommendations
- [ ] Real-time price tracking and alerts
- [ ] Collaborative trip planning features
- [ ] Advanced analytics and user insights

### Long-term (6-12 months)
- [ ] Mobile application development
- [ ] Enterprise features and API marketplace
- [ ] Advanced AI with preference learning
- [ ] Global destination expansion

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google ADK team for the excellent development framework
- OpenWeatherMap for reliable weather data
- Unsplash for beautiful destination photography
- The open-source community for invaluable tools and libraries

---

**Made with ❤️ for intelligent travel planning**

For detailed development documentation, see [Travel_AI_Agent.md](Travel_AI_Agent.md) | For technical improvements, see [COMPREHENSIVE_IMPROVEMENTS_SUMMARY.md](COMPREHENSIVE_IMPROVEMENTS_SUMMARY.md)
