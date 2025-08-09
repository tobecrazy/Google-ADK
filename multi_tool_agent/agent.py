import os
from typing import Any, List

from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from google.adk.tools.mcp_tool import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_toolset import StdioServerParameters
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from google.genai import types
from rich import print

# Load environment variables from the .env file in the same directory
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

def create_mcp_toolsets() -> List[MCPToolset]:
    """Creates MCP toolsets without connecting to them yet."""
    toolsets = []
    
    # Create HTTP stream server toolset (but don't connect yet)
    try:
        amap_api_key = os.getenv('AMAP_API_KEY')
        if not amap_api_key:
            print("Warning: AMAP_API_KEY not found in environment variables")
            return toolsets
        
        http_toolset = MCPToolset(
            connection_params=StreamableHTTPServerParams(
                url=f"https://mcp.amap.com/mcp?key={amap_api_key}",
            )
        )
        toolsets.append(http_toolset)
        print("HTTP MCP Toolset configured.")
    except Exception as e:
        print(f"Warning: Could not configure HTTP MCP toolset: {e}")
    
    # Create stdio server toolset (time server) - use uvx instead of python -m
    try:
        stdio_toolset = MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='uvx',
                    args=['mcp-server-time', '--local-timezone=Asia/Shanghai'],
                )
            )
        )
        toolsets.append(stdio_toolset)
        print("Stdio MCP Toolset configured.")
    except Exception as e:
        print(f"Warning: Could not configure stdio MCP toolset: {e}")
    
    return toolsets

def create_agent() -> LlmAgent:
    """Creates an ADK Agent with MCP toolsets (lazy loading)."""
    toolsets = create_mcp_toolsets()
    
    root_agent = LlmAgent(
        model=LiteLlm(model="ollama/qwen3:32b"),
        name="assistant",
        instruction="""You are a helpful assistant that can help users with various tasks using available MCP tools.
        
        Available tools may include:
        - Maps and location tools from AMap
        - Time-related tools for getting current time and time conversions
        
        When helping users:
        1. Use the available MCP tools to gather information
        2. Provide clear and comprehensive responses based on the information retrieved
        3. If asked to summarize content, do so using your natural language capabilities
        4. Always be helpful and informative in your responses
        
        Note: You should use the available MCP tools to gather data, then provide summaries and explanations using your own capabilities.
        """,
        tools=toolsets,  # Pass toolsets directly - they will be loaded when needed
    )
    print(f"Agent created with {len(toolsets)} MCP toolsets.")
    return root_agent

# Create the root_agent without async issues during module loading
root_agent = create_agent()
