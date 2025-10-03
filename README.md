# Google ADK Travel AI Agent

An intelligent travel planning assistant built with Google ADK (AI Development Kit) and enhanced with MCP (Model Context Protocol) tool integration for real-time data access.

## 🌟 Features

### Core Capabilities
- **🧠 Intelligent Travel Planning**: Generate comprehensive travel itineraries with attractions, accommodations, dining, and transportation
- **📅 Smart Date Parsing**: Automatically handle relative dates like "后天" (day after tomorrow), "明天" (tomorrow), "3天后" (in 3 days)
- **💰 Budget Optimization**: Create multiple plan options (economic and premium) based on your budget
- **📊 Visual & Markdown Reports**: Generate beautiful HTML and detailed Markdown reports with images and information
- **🌐 Real-time Data**: Access current weather, maps, and location data through MCP tools. AttractionService now uses real-time data from Amap MCP.

### MCP Tool Integration
- **⏰ Time Server**: Accurate date/time calculations with timezone support
- **🗺️ Amap Maps**: Location search, weather forecasts (exclusive source), real-time attraction data, and route planning
- **🌐 Web Fetch**: Real-time web data retrieval for restaurant pages and image searches
- **🧠 Memory**: User preferences and travel history storage
- **🖼️ Image Services**: Enhanced image search and retrieval using MCP fetch capabilities
- **🔄 Async Loading**: Parallel tool initialization for optimal performance

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js (for MCP servers)
- ModelScope API Key (for open-source models)
- Amap API Key (optional, for enhanced location services)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tobecrazy/Google-ADK.git
   cd Google-ADK
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install MCP dependencies**
   ```bash
   # Install uvx for Python-based MCP servers
   pip install uv
   
   # Install Node.js MCP servers
   npm install -g @modelcontextprotocol/server-memory
   npm install -g @amap/amap-maps-mcp-server
   ```

4. **Configure environment variables**
   ```bash
   cd travel_agent
   cp .env.example .env
   # Edit .env with your API keys
   ```

### Environment Configuration

Create a `.env` file in the `travel_agent` directory:

```env
# Required: ModelScope API Key for open-source models
MODELSCOPE_API_KEY=your_modelscope_api_key_here

# Optional: Amap API Key for enhanced location services
AMAP_MAPS_API_KEY=your_amap_api_key_here

# Optional: Other service API keys
OPENWEATHER_API_KEY=your_openweather_key_here

# MCP Configuration (to prevent timeout issues)
MCP_TIMEOUT=30
MCP_RETRIES=3
MCP_LOG_LEVEL=info

# LiteLLM Configuration
LITELLM_LOG=ERROR
LITELLM_MAX_RETRIES=3
LITELLM_TIMEOUT=30

# Travel Agent Settings
DEFAULT_TIMEZONE=Asia/Shanghai
DEFAULT_CURRENCY=CNY
CACHE_ENABLED=true
CACHE_TTL=3600
```

### Model Update

The travel agent now uses ModelScope open-source models for enhanced performance and fallback options. The models are configured to automatically switch in case of rate limits, ensuring continuous operation. This represents a major upgrade from Google's Gemini models to Chinese open-source alternatives including Qwen and DeepSeek models.

### Usage Instructions

Ensure all environment variables are set correctly in the `.env` file. The agent now supports advanced model configurations and MCP tool integrations for real-time data access.

## 🛠️ Usage

### Basic Usage

```python
from travel_agent.agent import create_robust_travel_agent

# Create the travel agent
agent, status = create_robust_travel_agent()

# Check MCP tool status
print(f"Available MCP tools: {status.get('successful_tools', [])}")
print(f"Total tools: {status.get('registry_status', {}).get('total_tools', 0)}")

# The agent is ready to use with Google ADK
```

### Advanced Usage with Async

```python
import asyncio
from travel_agent.agent import create_travel_agent_async

async def main():
    # Create agent asynchronously for better performance
    agent, status = await create_travel_agent_async()
    
    # Check detailed status
    if not status.get('fallback_mode'):
        registry_status = status.get('registry_status', {})
        print(f"MCP Tools by Server:")
        for server, count in registry_status.get('tools_by_server', {}).items():
            print(f"  - {server}: {count} tools")

asyncio.run(main())
```

### Testing MCP Integration

```bash
cd travel_agent
python test_mcp_simple.py
```

Expected output:
```
🚀 Starting Simple MCP Tests
==================================================
📋 Test 1: Configuration loading
Found 3 base configurations:
  - Time Server (required)
  - Fetch Server (optional)
  - Memory Server (optional)
  - Amap Maps Server (optional, API key found)

🔧 Test 2: Async tool initialization
Initialization results:
  - Successful: ['Time Server', 'Fetch Server', 'Memory Server', 'Amap Maps Server']
  - Failed: []
  - Success rate: 100.00%

📋 Test 3: Tool registry
Registry status:
  - Total tools: 14
  - Tools by server: {'Time Server': 2, 'Fetch Server': 1, 'Memory Server': 3, 'Amap Maps Server': 8}

🎉 Core functionality tests passed!
```

## 🏗️ Architecture

### MCP Tool Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Travel AI Agent                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ TravelAgent     │  │ DataCollector   │  │ ReportGen   │  │
│  │ Builder         │  │ Agent           │  │ Agent       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                   MCP Tool Registry                         │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Async Tool Initialization & Management                  │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
│  │ Time Server │ │ Amap Maps   │ │ Web Fetch   │ │ Memory │ │
│  │ (uvx)       │ │ (npm)       │ │ (uvx)       │ │ (npm)  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **MCPToolConfig**: Centralized configuration management
2. **AsyncMCPToolInitializer**: Parallel tool initialization with error handling
3. **MCPToolRegistry**: Unified tool registration and async calling
4. **TravelAgentBuilder**: Clean agent construction with MCP integration

## 📋 Available MCP Tools

### Time Server (Required)
- `get_current_time`: Get current time in specified timezone
- `convert_time`: Convert time between timezones

### Amap Maps Server (Optional)
- `maps_weather`: Weather forecasts for destinations
- `maps_text_search`: Search for points of interest
- `maps_around_search`: Find nearby locations
- `maps_geo`: Geocoding (address to coordinates)
- `maps_regeocode`: Reverse geocoding (coordinates to address)
- `maps_direction_driving`: Driving directions
- `maps_direction_walking`: Walking directions
- `maps_search_detail`: Detailed POI information

### Web Fetch Server (Optional)
- `fetch`: Retrieve and process web content, restaurant pages, and image searches

### Memory Server (Optional)
- `create_entities`: Store travel preferences
- `search_nodes`: Search stored information
- `open_nodes`: Retrieve specific data

## 🔧 Configuration

### MCP Server Configuration

The system automatically configures MCP servers based on available dependencies and API keys:

```python
# Base configurations (always attempted)
- Time Server: uvx mcp-server-time --local-timezone=Asia/Shanghai
- Fetch Server: uvx mcp-server-fetch  
- Memory Server: npx -y @modelcontextprotocol/server-memory

# Conditional configurations (based on API keys)
- Amap Maps: npx -y @amap/amap-maps-mcp-server (requires AMAP_MAPS_API_KEY)
```

### Fallback Behavior

The system provides graceful degradation:
- **Required tools fail**: Agent switches to fallback mode
- **Optional tools fail**: Agent continues with available tools
- **All tools fail**: Agent uses AI-generated content only

## 🧪 Testing

### Run All Tests
```bash
cd travel_agent
python test_mcp_simple.py
```

### Test Individual Components
```bash
# Test configuration loading
python -c "from agent import MCPToolConfig; print(MCPToolConfig.get_base_configs())"

# Test async initialization
python -c "import asyncio; from agent import AsyncMCPToolInitializer; asyncio.run(AsyncMCPToolInitializer().initialize_all_tools_async())"
```

## 🚨 Troubleshooting

### Common Issues

1. **MCP Server Not Found**
   ```
   Command 'uvx' not found
   ```
   **Solution**: Install uv: `pip install uv`

2. **Amap API Key Issues**
   ```
   Amap Maps API key not found or invalid
   ```
   **Solution**: Set `AMAP_MAPS_API_KEY` in your `.env` file

3. **Tool Initialization Timeout**
   ```
   Tool initialization timeout
   ```
   **Solution**: Check internet connection and increase timeout in config

4. **Import Errors**
   ```
   No module named 'travel_agent'
   ```
   **Solution**: Run from the correct directory and check Python path

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 Recent Updates

### v2.3.0 - LLM Migration to ModelScope Open-Source Models
- ✅ **LLM Migration**: Complete migration from Google's Gemini models to ModelScope open-source models (Qwen, DeepSeek)
- ✅ **Enhanced Performance**: Improved response times and reduced dependency on external APIs
- ✅ **Domestic Model Support**: Integration with Chinese open-source models for better cultural and linguistic context
- ✅ **Fallback Model System**: Automatic switching between models (Qwen, DeepSeek) in case of rate limits
- ✅ **API Configuration Update**: Changed from GOOGLE_API_KEY to MODELSCOPE_API_KEY requirement

### v2.2.0 - Enhanced Web Fetch and Content Integration
- ✅ **MCP Fetch Service Integration**: Added `MCPFetchService` and `MCPImageService` for enhanced content and image retrieval capabilities.
- ✅ **Restaurant Data Enhancement**: Updated `restaurant_scraper.py` to use MCP services for fetching restaurant pages and images with intelligent fallback logic.
- ✅ **Improved URL Handling**: Enhanced URL processing and DuckDuckGo redirect parsing for more reliable web content fetching.
- ✅ **Image Search Capabilities**: New image search functionality using MCP fetch for restaurants, attractions, and food items.
- ✅ **Python Publishing Workflow**: Added automated GitHub Actions workflow for Python package publishing.

### v2.1.0 - Real-time Data and Reporting Enhancements
- ✅ **Real-time Attraction Data**: `AttractionService` now retrieves real-time attraction information using Amap MCP, providing more accurate and up-to-date recommendations.
- ✅ **Markdown Report Generation**: In addition to HTML, the agent now generates detailed travel reports in Markdown format.
- ✅ **Streamlined Weather Service**: `WeatherService` has been refactored to exclusively use the Amap MCP server for all weather data, simplifying the architecture.
- ✅ **Improved Cost Display**: The HTML travel plan reports now feature enhanced display logic for estimated costs, improving clarity for users.

### v2.0.0 - MCP Tool Integration Optimization
- ✅ **Async Tool Loading**: Parallel initialization of MCP servers
- ✅ **Clean Architecture**: Separated concerns with dedicated classes
- ✅ **Error Handling**: Comprehensive error handling and fallback mechanisms
- ✅ **Tool Registry**: Unified tool management and calling interface
- ✅ **Configuration Management**: Centralized MCP server configuration
- ✅ **Testing Framework**: Comprehensive test suite for MCP integration
- ✅ **Performance**: 100% success rate in tool initialization
- ✅ **Compatibility**: Backward compatibility with existing code

### Key Improvements
- **ModelScope Integration**: Complete migration to Chinese open-source models (Qwen, DeepSeek) from Google's Gemini
- **4+ MCP servers** successfully integrated (Time, Amap Maps, Web Fetch, Memory, Image Services)
- **15+ total tools** available for real-time data access and content retrieval
- **Enhanced web scraping** with MCP fetch service integration
- **Intelligent image search** for restaurants, attractions, and food items
- **Async/await pattern** for optimal performance
- **Graceful degradation** when tools are unavailable
- **Detailed status reporting** for debugging and monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google ADK team for the AI development framework
- ModelScope team for open-source large language models
- Model Context Protocol (MCP) for tool integration standards
- Amap for location and weather services
- Open source community for MCP server implementations

---

**Note**: This project uses experimental features from Google ADK and MCP. Some functionality may change in future versions.
