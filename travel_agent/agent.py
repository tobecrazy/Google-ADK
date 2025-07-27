"""
Travel AI Agent - Google ADK Integration with MCP (Robust Version)
Fixed version that handles MCP connection issues gracefully
"""

import os
import logging
import asyncio
from typing import List, Optional
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from .main import create_travel_planning_tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from travel_agent/.env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class SafeMCPManager:
    """Manages MCP connections with robust error handling and fallback mechanisms"""
    
    def __init__(self):
        self.available_tools = []
        self.failed_connections = []
        
    def create_mcp_toolset(self, name: str, command: str, args: List[str], 
                          env_vars: Optional[dict] = None, 
                          tool_filter: Optional[List[str]] = None,
                          timeout: int = 10) -> Optional[MCPToolset]:
        """Create MCP toolset with comprehensive error handling"""
        try:
            logger.info(f"🔄 Attempting to configure MCP toolset: {name}")
            
            # Test if command is available first
            import subprocess
            try:
                test_result = subprocess.run(
                    [command] + args + ['--help'], 
                    capture_output=True, 
                    text=True, 
                    timeout=timeout
                )
                if test_result.returncode != 0:
                    logger.warning(f"⚠️  Command test failed for {name}: {test_result.stderr}")
                    self.failed_connections.append(f"{name}: Command not available")
                    return None
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️  Command test timeout for {name}")
                self.failed_connections.append(f"{name}: Command timeout")
                return None
            except Exception as e:
                logger.warning(f"⚠️  Command test error for {name}: {e}")
                self.failed_connections.append(f"{name}: {str(e)}")
                return None
            
            # Create connection parameters
            connection_params = StdioServerParameters(
                command=command,
                args=args,
                env=env_vars or {}
            )
            
            # Create toolset
            toolset = MCPToolset(
                connection_params=connection_params,
                tool_filter=tool_filter or []
            )
            
            logger.info(f"✅ Successfully configured MCP toolset: {name}")
            self.available_tools.append(name)
            return toolset
            
        except Exception as e:
            error_msg = f"Failed to configure {name}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.failed_connections.append(error_msg)
            return None
    
    def get_status_report(self) -> dict:
        """Get a status report of MCP connections"""
        return {
            'available_tools': self.available_tools,
            'failed_connections': self.failed_connections,
            'total_attempted': len(self.available_tools) + len(self.failed_connections),
            'success_rate': len(self.available_tools) / max(1, len(self.available_tools) + len(self.failed_connections))
        }

def create_robust_travel_agent():
    """Create travel agent with robust MCP handling"""
    
    mcp_manager = SafeMCPManager()
    mcp_tools = []
    
    # Define MCP server configurations
    mcp_configs = [
        {
            'name': 'Time Server',
            'command': 'uvx',
            'args': ['mcp-server-time', '--local-timezone=Asia/Shanghai'],
            'env_vars': {},
            'tool_filter': ['get_current_time', 'convert_time'],
            'priority': 'high'  # Essential for date parsing
        },
        {
            'name': 'Fetch Server',
            'command': 'uvx', 
            'args': ['mcp-server-fetch'],
            'env_vars': {},
            'tool_filter': ['fetch'],
            'priority': 'medium'
        },
        {
            'name': 'Memory Server',
            'command': 'npx',
            'args': ['-y', '@modelcontextprotocol/server-memory'],
            'env_vars': {},
            'tool_filter': ['create_entities', 'search_nodes', 'open_nodes'],
            'priority': 'low'
        }
    ]
    
    # Add Amap server only if API key is available
    amap_api_key = os.getenv('AMAP_MAPS_API_KEY', '')
    if amap_api_key and amap_api_key != 'your_amap_api_key_here':
        mcp_configs.append({
            'name': 'Amap Maps Server',
            'command': 'npx',
            'args': ['-y', '@amap/amap-maps-mcp-server'],
            'env_vars': {'AMAP_API_KEY': amap_api_key},
            'tool_filter': [
                'maps_text_search',
                'maps_around_search', 
                'maps_geo',
                'maps_regeocode',
                'maps_search_detail',
                'maps_weather',
                'maps_direction_driving',
                'maps_direction_walking'
            ],
            'priority': 'high'  # Important for location services
        })
    else:
        logger.warning("⚠️  Amap Maps API key not found, skipping Amap MCP server")
    
    # Try to create each MCP toolset
    for config in mcp_configs:
        toolset = mcp_manager.create_mcp_toolset(
            name=config['name'],
            command=config['command'],
            args=config['args'],
            env_vars=config['env_vars'],
            tool_filter=config['tool_filter']
        )
        if toolset:
            mcp_tools.append(toolset)
    
    # Get status report
    status = mcp_manager.get_status_report()
    logger.info(f"🔧 MCP Status: {status['available_tools']} available, "
               f"{len(status['failed_connections'])} failed")
    
    if status['failed_connections']:
        logger.warning("⚠️  Failed MCP connections:")
        for failure in status['failed_connections']:
            logger.warning(f"   - {failure}")
    
    # Add the original travel planning tool
    all_tools = mcp_tools + [create_travel_planning_tool]
    
    # Create enhanced instruction based on available tools
    instruction_parts = [
        "You are an expert travel planning assistant with the following capabilities:",
        "1. INTELLIGENT DATE PARSING: When users mention relative dates like '后天' (day after tomorrow), "
        "'明天' (tomorrow), or '3天后' (in 3 days), automatically calculate the correct date based on "
        "the current system time. NEVER use hardcoded dates.",
        "2. COMPREHENSIVE PLANNING: Generate detailed travel plans that include attractions, "
        "accommodations, dining, transportation (高铁, 航班, 自驾, 客车), and budget optimization.",
        "3. VISUAL REPORTS: Create beautiful HTML reports with images and detailed information.",
        "4. MULTIPLE OPTIONS: Always provide multiple travel plan options (economic and comfort).",
        "5. CURRENT CONTEXT: Always consider the current date and time when planning travel dates."
    ]
    
    # Add tool-specific instructions based on what's available
    if 'Time Server' in status['available_tools']:
        instruction_parts.append("6. REAL-TIME DATES: Use the time server to get accurate current time for date calculations.")
    
    if 'Amap Maps Server' in status['available_tools']:
        instruction_parts.append("7. LOCATION SERVICES: Use Amap maps tools for accurate location information, POI search, and route planning.")
    
    if 'Fetch Server' in status['available_tools']:
        instruction_parts.append("8. WEB DATA: Use fetch tools to get real-time information when needed.")
    
    if 'Memory Server' in status['available_tools']:
        instruction_parts.append("9. MEMORY: Use memory tools to store and recall travel preferences and past interactions.")
    
    # Add fallback instruction
    instruction_parts.append(
        f"10. GRACEFUL DEGRADATION: If MCP tools fail, continue with AI-generated content and inform the user. "
        f"Currently available: {', '.join(status['available_tools']) if status['available_tools'] else 'None'}"
    )
    
    instruction = "\n".join(instruction_parts)
    
    logger.info(f"🚀 Creating agent with {len(mcp_tools)} MCP toolsets and 1 travel planning tool")
    
    return LlmAgent(
        name="travel_planning_agent",
        model="gemini-2.0-flash",
        instruction=instruction,
        tools=all_tools,
    ), status

# Create the agent with error handling
try:
    root_agent, mcp_status = create_robust_travel_agent()
    logger.info("✅ Travel agent created successfully")
    logger.info(f"📊 MCP Tools Status: {mcp_status}")
except Exception as e:
    logger.error(f"❌ Failed to create travel agent: {e}")
    # Create a minimal agent with just the travel planning tool
    logger.info("🔄 Creating fallback agent with minimal tools...")
    root_agent = LlmAgent(
        name="travel_planning_agent_fallback",
        model="gemini-2.0-flash",
        instruction=(
            "You are an expert travel planning assistant. Generate detailed travel plans "
            "that include attractions, accommodations, dining, transportation, and budget "
            "optimization. Always provide multiple travel plan options (economic and comfort) "
            "and create beautiful HTML reports with images and detailed information. "
            "Note: MCP tools are currently unavailable, using AI-generated content."
        ),
        tools=[create_travel_planning_tool],
    )
    logger.info("✅ Fallback travel agent created successfully")
