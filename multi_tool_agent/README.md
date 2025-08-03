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
* **Gemini 2.0 Flash**: The LLM model used for processing and analysis

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
4. Run the agent server
5. Start interacting with the multi-tool capabilities

For more detailed information about the Google ADK framework and MCP integration, refer to the main project documentation.
