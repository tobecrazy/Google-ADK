import os
from typing import Any, List
import time

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

def create_llm_model() -> LiteLlm:
    """Creates a LiteLLM model with fallback options for rate limits."""
    
    # List of models to try in order (most reliable and least rate-limited first)
    models_to_try = [
        "openrouter/moonshotai/kimi-k2:free",
        "openrouter/qwen/qwen3-235b-a22b:free",
        "openrouter/deepseek/deepseek-chat-v3-0324:free"     
    ]
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    for i, model in enumerate(models_to_try):
        try:
            print(f"Attempting to create model with: {model} (attempt {i+1}/{len(models_to_try)})")
            llm_model = LiteLlm(
                model=model,
                api_key=api_key,
                api_base="https://openrouter.ai/api/v1",
                max_retries=2,  # Reduced retries to fail faster
                timeout=30
            )
            print(f"✅ Successfully created model with: {model}")
            return llm_model
        except Exception as e:
            print(f"❌ Failed to create model with {model}: {str(e)[:100]}...")
            if model != models_to_try[-1]:  # Not the last model
                print(f"⏭️  Trying next model in {2}s...")
                time.sleep(2)  # Brief delay before trying next model
            continue
    
    # If all models fail, raise an exception
    raise RuntimeError("❌ All model options failed. Please check your API key and try again later.")

def create_agent() -> LlmAgent:
    """Creates an ADK Agent with MCP toolsets (lazy loading)."""
    toolsets = create_mcp_toolsets()
    
    # Create model with fallback options
    model = create_llm_model()
    
    root_agent = LlmAgent(
        model=model,
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
        5. If you encounter rate limits, please wait a moment and try again
        
        Note: You should use the available MCP tools to gather data, then provide summaries and explanations using your own capabilities.
        """,
        tools=toolsets,  # Pass toolsets directly - they will be loaded when needed
    )
    print(f"Agent created with {len(toolsets)} MCP toolsets.")
    return root_agent

# Create the root_agent without async issues during module loading
root_agent = create_agent()
