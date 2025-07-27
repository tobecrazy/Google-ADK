"""
Travel AI Agent - Google ADK Integration with MCP
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from .main import create_travel_planning_tool

# Load environment variables from travel_agent/.env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Define absolute paths for MCP servers
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

root_agent = LlmAgent(
    name="travel_planning_agent",
    model="gemini-2.0-flash",
    instruction=(
        "You are an expert travel planning assistant with advanced MCP-powered capabilities:\n"
        "1. INTELLIGENT DATE PARSING: When users mention relative dates like '后天' (day after tomorrow), "
        "'明天' (tomorrow), or '3天后' (in 3 days), automatically calculate the correct date based on "
        "the current system time. NEVER use hardcoded dates like '2024-07-08'.\n"
        "2. REAL-TIME ATTRACTION DATA: Use MCP tools to search for real attractions, POIs, and location data "
        "based on the actual destination city. Never use hardcoded attractions.\n"
        "3. COMPREHENSIVE PLANNING: Generate detailed travel plans that include attractions, "
        "accommodations, dining, transportation (高铁, 航班, 自驾, 客车), and budget optimization.\n"
        "4. LOCATION SERVICES: Use maps and geocoding tools to provide accurate location information, "
        "distances, and nearby recommendations.\n"
        "5. VISUAL REPORTS: Create beautiful HTML reports with images and detailed information.\n"
        "6. MULTIPLE OPTIONS: Always provide multiple travel plan options (economic and comfort).\n"
        "7. CURRENT CONTEXT: Always consider the current date and time when planning travel dates.\n"
        "8. MCP INTEGRATION: Leverage MCP tools for real-time data including maps, time, weather, and more."
    ),
    tools=[
        # Amap Maps MCP Server for real attraction and location data
        MCPToolset(
            connection_params=StdioServerParameters(
                command='npx',
                args=[
                    '-y',
                    '@amap/amap-maps-mcp-server'
                ],
                env={
                    'AMAP_API_KEY': os.getenv('AMAP_MAPS_API_KEY', '')
                }
            ),
            # Filter to expose only the tools we need for travel planning
            tool_filter=[
                'maps_text_search',
                'maps_around_search', 
                'maps_geo',
                'maps_regeocode',
                'maps_search_detail'
            ]
        ),
        
        # Time MCP Server for timezone and date handling
        MCPToolset(
            connection_params=StdioServerParameters(
                command='uvx',
                args=[
                    'mcp-server-time',
                    '--local-timezone=Asia/Shanghai'
                ]
            ),
            tool_filter=['get_current_time', 'convert_time']
        ),
        
        # Fetch MCP Server for web scraping travel data
        MCPToolset(
            connection_params=StdioServerParameters(
                command='uvx',
                args=['mcp-server-fetch']
            ),
            tool_filter=['fetch']
        ),
        
        # Memory MCP Server for caching travel preferences
        MCPToolset(
            connection_params=StdioServerParameters(
                command='npx',
                args=[
                    '-y',
                    '@modelcontextprotocol/server-memory'
                ]
            ),
            tool_filter=[
                'create_entities',
                'search_nodes',
                'open_nodes'
            ]
        ),
        
        # Original travel planning tool
        create_travel_planning_tool,
    ],
)
