# Wikipedia Article Extractor and Summarizer Agent

This agent helps you extract and summarize articles from Wikipedia links. It can also provide current time information for different timezones. The agent uses MCP (Model Context Protocol) tools to fetch content and provide accurate information.

## Features

*   **Wikipedia Article Extraction:** Extracts content from Wikipedia articles using provided links.
*   **Intelligent Summarization:** Summarizes extracted articles in a few concise sentences.
*   **Time Information:** Provides current time information for different timezones.
*   **MCP Integration:** Uses Google ADK's native MCPToolset integration for tool management.

## How to Use

1.  **Configure Environment Variables:**
    Create a `.env` file in the `multi_tool_agent/` directory with the following variables:
    ```bash
    GOOGLE_GENAI_USE_VERTEXAI=FALSE
    GOOGLE_API_KEY=your_google_api_key_here
    AMAP_API_KEY=your_amap_api_key_here
    ```

2.  **Run the Agent Server:**
    ```bash
    mcp run -p 8000 multi_tool_agent.agent:app
    ```

3.  **Interact with the Agent:**
    Send messages to the agent with:
    *   Wikipedia links for article extraction and summarization
    *   Requests for current time in different timezones

    **Example interactions:**
    *   "Extract and summarize this article: https://en.wikipedia.org/wiki/Artificial_intelligence"
    *   "What time is it in New York?"

## Technology Stack

*   **Google ADK:** The core framework for building the agent.
*   **MCP Tools:** 
    *   HTTP Stream Server for Wikipedia extraction
    *   Time Server (mcp_server_time) for time information
*   **Gemini 2.0 Flash:** The LLM model used for processing and summarization.

## MCP Tool Configuration

The agent is configured with two MCP tool sources:

1.  **HTTP Stream Server:**
    *   URL: `https://mcp.amap.com/mcp?key=${AMAP_API_KEY}`
    *   Provides Wikipedia extraction capabilities
    *   Requires AMAP_API_KEY environment variable

2.  **Stdio Server (Time Server):**
    *   Command: `uvx mcp-server-time --local-timezone=Asia/Shanghai`
    *   Provides time information capabilities

## Environment Variables

The following environment variables are required:

*   **GOOGLE_API_KEY:** Your Google Gemini API key for the LLM model
*   **AMAP_API_KEY:** Your AMap API key for location and mapping services
*   **GOOGLE_GENAI_USE_VERTEXAI:** Set to FALSE to use Google AI Studio instead of Vertex AI
