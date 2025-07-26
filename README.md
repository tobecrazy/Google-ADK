# Google ADK Project

This project provides tools and utilities for working with Google's AI Development Kit (ADK), featuring an intelligent Travel Planning AI Agent that generates comprehensive travel itineraries with real-time data integration and enhanced Chinese language support.

## Project Components

### 1. Multi-Tool Agent
Basic weather and time query agent for demonstration purposes.

### 2. Travel AI Agent ⭐ (Featured)
An intelligent travel planning AI Agent that automatically generates illustrated HTML travel planning reports with real attraction images, comprehensive transportation planning, smart date parsing, and accurate weather forecasts. Fully supports Chinese language input and relative date expressions.

## Project Structure

```
.
├── GEMINI.md                    # Documentation for Gemini integration
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── Travel_AI_Agent.md          # Detailed project requirements
├── multi_tool_agent/           # Basic demo agent
│   ├── __init__.py
│   ├── agent.py                # Weather and time agent
│   ├── data_layer.py           # Knowledge graph utilities
│   └── README.md
└── travel_agent/               # Travel AI Agent (Main Project)
    ├── .env                    # API keys configuration
    ├── main.py                 # ADK entry point
    ├── agents/
    │   ├── travel_planner.py   # Core planning agent
    │   ├── data_collector.py   # Data collection agent
    │   └── report_generator.py # HTML report generator
    ├── services/
    │   ├── weather_service.py  # Weather API integration
    │   ├── attraction_service.py # POI data service
    │   ├── transport_service.py # Transportation service
    │   └── accommodation_service.py # Hotel/lodging service
    ├── utils/
    │   ├── web_scraper.py      # Web scraping utilities
    │   ├── image_handler.py    # Image processing
    │   └── budget_calculator.py # Budget optimization
    ├── templates/
    │   └── travel_plan.html    # HTML report template
    └── output/                 # Generated travel reports
```

## Travel AI Agent Features

### 🎯 Core Features
- 🌍 **Intelligent Destination Analysis** - Comprehensive destination research and insights
- 📅 **Smart Date Parsing** - Supports relative dates like "今天", "明天", "后天" with real-time system date integration
- 💰 **Budget Optimization** - Smart budget allocation (30% transport, 35% accommodation, 20% dining, 15% attractions)
- 🗺️ **Route Optimization** - Geographic clustering and efficient routing
- 📊 **Rich HTML Reports** - Beautiful, responsive, printable travel reports with real images

### 🚗 Transportation Planning
- **自驾 (Self-driving)** - Route planning, fuel costs, tolls, parking estimates
- **高铁 (High-speed rail)** - Schedules, booking info, seat types, station details
- **飞机 (Airplane)** - Flight options, airports, baggage policies, timing recommendations
- **Comprehensive Analysis** - Detailed pros/cons, costs, and booking information for each option

### 🏛️ Enhanced Attraction Experience
- **Real Images** - Integration with Unsplash API for authentic attraction photos
- **Detailed Information** - Opening hours, ticket prices, visitor tips
- **Smart Keywords** - Optimized image search for better visual matching
- **Fallback Design** - Elegant styled placeholders when images unavailable

### 🌤️ Weather Intelligence
- **Real-time Forecasts** - OpenWeatherMap API integration with 7-day forecasts
- **Chinese City Support** - Enhanced handling of Chinese city names with Pinyin conversion
- **Seasonal Patterns** - Intelligent fallback with realistic seasonal weather data
- **Activity Planning** - Weather-based activity recommendations

### 🏨 Accommodation & Dining
- **Hotel Recommendations** - Budget-appropriate lodging options with photos and locations
- **Local Cuisine** - Restaurant suggestions with photos, prices, and specialties
- **Cultural Integration** - Local dining customs and food recommendations

### 🌐 Language & Localization
- **Full Chinese Support** - Native Chinese language processing and output
- **Date Localization** - Smart parsing of Chinese relative date expressions
- **Cultural Context** - Location-appropriate recommendations and cultural insights

## Requirements

### Python Version
- Python 3.9 or higher

### API Keys Required
Configure these in `travel_agent/.env`:
- `GOOGLE_API_KEY` - For Gemini AI model
- `OPENWEATHER_API_KEY` - For weather data
- `FIRECRAWL_API_KEY` - For web scraping (optional)

### Python Libraries
All dependencies are listed in `requirements.txt` including:
- `google-adk` - Google ADK framework
- `google-generativeai` - Gemini AI integration
- `beautifulsoup4` & `lxml` - Web scraping and HTML parsing
- `jinja2` - HTML templating engine
- `pillow` - Image processing and handling
- `selenium` & `webdriver_manager` - Advanced web scraping
- `pypinyin` - Chinese text processing and Pinyin conversion
- `python-dateutil` & `pytz` - Advanced date parsing and timezone handling
- `httpx` & `aiohttp` - Async HTTP client libraries
- `tenacity` - Retry logic and error handling
- `crawl4ai` & `markdownify` - Enhanced web crawling capabilities
- `fastapi` & `uvicorn` - Web API framework (for future extensions)
- `python-dotenv` - Environment variable management

## Installation

1. Clone this repository:
```bash
git clone https://github.com/tobecrazy/Google-ADK.git
cd Google-ADK
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure API keys in `travel_agent/.env`:
```bash
cp travel_agent/.env.example travel_agent/.env
# Edit travel_agent/.env with your API keys
```

## Usage

### Travel AI Agent

```python
from travel_agent.main import TravelAgent

# Initialize the agent
agent = TravelAgent()

# Generate travel plan
result = agent.plan_travel(
    destination="Tokyo, Japan",
    departure_location="Shanghai, China", 
    start_date="2024-03-15",
    duration=7,
    budget=8000
)

# The agent will generate an HTML report in travel_agent/output/
```

### Multi-Tool Agent (Demo)

```python
from multi_tool_agent.agent import root_agent

# Query weather
response = root_agent.query("What's the weather in Shanghai?")
print(response)
```

## API Configuration

Create `travel_agent/.env` with the following structure:

```bash
# AI Model Configuration
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_google_api_key_here

# Weather Service
OPENWEATHER_API_KEY=your_openweather_api_key

# Web Scraping (Optional)
FIRECRAWL_API_KEY=your_firecrawl_api_key

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
CACHE_TIMEOUT=3600
MAX_CONCURRENT_REQUESTS=10
```

## Example Output

The Travel AI Agent generates comprehensive HTML reports including:

### 📋 Travel Overview
- Destination information with cultural context
- Smart date parsing (supports "明天", "后天" etc.)
- Comprehensive budget summary and allocation

### 🚗 Transportation Planning (NEW!)
- **Three detailed options**: 自驾, 高铁, 飞机
- **Cost analysis**: Fuel, tickets, parking, tolls
- **Pros & Cons**: Detailed comparison for each transport mode
- **Booking information**: Practical tips and reservation details

### 🏛️ Attraction Experience (ENHANCED!)
- **Real photos**: Authentic images from Unsplash API
- **Detailed information**: Hours, prices, visitor tips
- **Cultural insights**: Historical context and significance
- **Smart recommendations**: Based on interests and budget

### 🌤️ Weather Integration (IMPROVED!)
- **7-day forecasts**: Real-time weather data
- **Chinese city support**: Enhanced city name recognition
- **Activity planning**: Weather-appropriate recommendations
- **Seasonal insights**: Climate patterns and best visit times

### 🏨 Accommodation & Dining
- **Hotel options**: Budget-appropriate with photos and locations
- **Local cuisine**: Restaurant recommendations with authentic photos
- **Cultural dining**: Local customs and specialty dishes
- **Price transparency**: Detailed cost breakdowns

### 📊 Smart Planning
- **Multiple itinerary options**: Economic vs. Comfort scenarios
- **Hour-by-hour scheduling**: Optimized daily plans
- **Budget optimization**: Intelligent cost allocation
- **Travel tips**: Practical advice and local insights

## Development

### Running Tests
```bash
# Run main functionality tests
python test_travel_agent.py

# Run improvement validation tests
python test_improvements.py

# Run with pytest (if available)
python -m pytest tests/
```

### Code Style
```bash
black travel_agent/
flake8 travel_agent/
```

### Recent Improvements Validation
The project includes comprehensive test suites that validate:
- ✅ Smart date parsing with Chinese relative dates
- ✅ Real-time weather data integration
- ✅ Attraction image fetching and display
- ✅ Transportation planning with three options
- ✅ End-to-end system integration

### Adding New Features
See [Travel_AI_Agent.md](Travel_AI_Agent.md) for detailed development guidelines and architecture.

## Documentation

- [Travel_AI_Agent.md](Travel_AI_Agent.md) - Comprehensive project requirements and development guide
- [GEMINI.md](GEMINI.md) - Gemini integration and coding preferences
- [multi_tool_agent/README.md](multi_tool_agent/README.md) - Basic agent implementation details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the documentation in [Travel_AI_Agent.md](Travel_AI_Agent.md)
2. Review existing issues on GitHub
3. Create a new issue with detailed information

## 🎉 Recent Updates (2025-07-26)

### Major Improvements Delivered
- ✅ **Real Attraction Images** - No more placeholder gradients, authentic photos via Unsplash API
- ✅ **Comprehensive Transportation** - Three detailed options (自驾/高铁/飞机) with costs and booking info
- ✅ **Smart Date Parsing** - Support for "今天", "明天", "后天" with real-time system date integration
- ✅ **Enhanced Weather** - Real OpenWeatherMap data with Chinese city support and Pinyin conversion
- ✅ **Full Chinese Localization** - Native Chinese language processing throughout the system

### Technical Enhancements
- Enhanced `TravelPlannerAgent` with advanced date parsing
- Improved `AttractionService` with image integration
- Upgraded `WeatherService` with multiple city query variations
- Enhanced HTML templates with transportation and image sections
- Comprehensive error handling and fallback mechanisms

---

**Note**: This project is designed for educational and demonstration purposes. The recent improvements make it production-ready for real travel planning scenarios. Ensure you comply with all API terms of service and website scraping policies when using the travel planning features.
