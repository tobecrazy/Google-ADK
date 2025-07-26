# Google ADK Project

This project provides tools and utilities for working with Google's AI Development Kit (ADK), featuring an intelligent Travel Planning AI Agent that generates comprehensive travel itineraries.

## Project Components

### 1. Multi-Tool Agent
Basic weather and time query agent for demonstration purposes.

### 2. Travel AI Agent ⭐ (Featured)
An intelligent travel planning AI Agent that automatically generates illustrated HTML travel planning reports based on user inputs including destination, travel dates, duration, and budget.

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

- 🌍 **Intelligent Destination Analysis** - Comprehensive destination research and insights
- 📅 **Personalized Itinerary Planning** - Day-by-day, hour-by-hour scheduling
- 💰 **Budget Optimization** - Smart budget allocation (30% transport, 35% accommodation, 20% dining, 15% attractions)
- 🗺️ **Route Optimization** - Geographic clustering and efficient routing
- 🏨 **Accommodation Recommendations** - Hotels and lodging within budget
- 🍽️ **Culinary Recommendations** - Local cuisine and restaurant suggestions
- 🌤️ **Weather Integration** - Weather-based activity planning
- 📊 **Rich HTML Reports** - Beautiful, responsive, printable travel reports
- 📱 **Multiple Planning Options** - Economic and comfort travel scenarios

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
- `beautifulsoup4` - Web scraping
- `jinja2` - HTML templating
- `pillow` - Image processing
- `selenium` - Advanced web scraping
- And more...

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

- **Travel Overview** - Destination info, dates, budget summary
- **Multiple Itinerary Options** - Economic vs. Comfort plans
- **Daily Schedules** - Hour-by-hour activity planning
- **Attraction Details** - Photos, descriptions, tickets, hours
- **Dining Recommendations** - Local cuisine with photos and prices
- **Accommodation Options** - Hotels with photos, prices, locations
- **Transportation Plans** - Routes, schedules, costs
- **Weather Forecast** - Daily weather for travel period
- **Budget Breakdown** - Detailed cost analysis
- **Travel Tips** - Practical advice and recommendations

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Style
```bash
black travel_agent/
flake8 travel_agent/
```

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

---

**Note**: This project is designed for educational and demonstration purposes. Ensure you comply with all API terms of service and website scraping policies when using the travel planning features.
