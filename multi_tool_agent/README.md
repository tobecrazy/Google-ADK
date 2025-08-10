# Multi-Tool Agent

A sophisticated AI agent that integrates multiple tools and services to provide comprehensive information gathering and analysis capabilities using MCP (Model Context Protocol) tools.

## Features

* **Multi-Tool Integration**: Seamlessly integrates various tools and APIs through MCP protocol
* **Time Information**: Provides current time information for different timezones
* **Flexible Architecture**: Modular design for easy extension and customization
* **MCP Integration**: Uses Google ADK's native MCPToolset integration for tool management

## How to Use

1. **Configure Environment Variables:**
   Create a `.env` file in the `multi_tool_agent/` directory with the following variables:
   ```bash
   GOOGLE_GENAI_USE_VERTEXAI=FALSE
   GOOGLE_API_KEY=your_google_api_key_here
   AMAP_API_KEY=your_amap_api_key_here
   ```

2. **Run the Agent Server:**
   ```bash
   mcp run -p 8000 multi_tool_agent.agent:app
   ```

3. **Interact with the Agent:**
   Send messages to the agent for various information requests:
   * Time queries for different timezones
   * General information gathering tasks
   * Data analysis and processing requests

   **Example interactions:**
   * "What time is it in New York?"
   * "Get current time in multiple timezones"

## Technology Stack

* **Google ADK**: The core framework for building the agent
* **MCP Tools**: 
  * HTTP Stream Server for web content extraction
  * Time Server (mcp_server_time) for time information
* **Meta Llama 3.1 8B**: The LLM model used for processing and analysis (via OpenRouter)
* **Model Fallback System**: Automatic fallback to alternative models if rate limits are encountered

## MCP Tool Configuration

The agent is configured with multiple MCP tool sources:

1. **HTTP Stream Server:**
   * URL: `https://mcp.amap.com/mcp?key=${AMAP_API_KEY}`
   * Provides web content extraction capabilities
   * Requires AMAP_API_KEY environment variable

2. **Stdio Server (Time Server):**
   * Command: `uvx mcp-server-time --local-timezone=Asia/Shanghai`
   * Provides time information capabilities

## Environment Variables

The following environment variables are required:

* **GOOGLE_API_KEY**: Your Google Gemini API key for the LLM model
* **AMAP_API_KEY**: Your AMap API key for location and mapping services
* **GOOGLE_GENAI_USE_VERTEXAI**: Set to FALSE to use Google AI Studio instead of Vertex AI

## Architecture

The multi-tool agent follows a modular architecture that allows for:

* Easy integration of new MCP tools
* Scalable processing capabilities
* Flexible configuration management
* Extensible functionality through plugin-like tool additions

## Getting Started

1. Clone the repository
2. Set up your environment variables
3. Install required dependencies
4. Test the agent: `python test_agent.py`
5. Run the agent server
6. Start interacting with the multi-tool capabilities

## Testing

Run the test script to verify your setup:

```bash
cd multi_tool_agent
python test_agent.py
```

This will verify that:
- Environment variables are properly configured
- The LLM model can be created successfully
- MCP toolsets are configured correctly
- The agent is ready to use

## Troubleshooting

### Rate Limit Issues
If you encounter rate limit errors:

1. **Automatic Fallback**: The agent now automatically tries multiple models in order:
   - `meta-llama/llama-3.1-8b-instruct:free` (primary)
   - `microsoft/phi-3-mini-128k-instruct:free` (fallback 1)
   - `google/gemma-2-9b-it:free` (fallback 2)
   - `qwen/qwen-2-7b-instruct:free` (fallback 3)

2. **Manual Model Selection**: You can uncomment alternative models in your `.env` file:
   ```bash
   # BACKUP_MODEL_1=openrouter/microsoft/phi-3-mini-128k-instruct:free
   # BACKUP_MODEL_2=openrouter/google/gemma-2-9b-it:free
   # BACKUP_MODEL_3=openrouter/qwen/qwen-2-7b-instruct:free
   ```

3. **Wait and Retry**: If all free models are rate-limited, wait a few minutes and try again.

### Common Issues
- **Missing API Keys**: Ensure `OPENROUTER_API_KEY` and `AMAP_API_KEY` are set in your `.env` file
- **Network Issues**: Check your internet connection for MCP tool initialization
- **MCP Tool Failures**: The agent will continue to work even if some MCP tools fail to initialize

For more detailed information about the Google ADK framework and MCP integration, refer to the main project documentation.
