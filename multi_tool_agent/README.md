# AI Travel Planner Agent

This agent helps you automatically plan your trip based on your destination, duration, and budget. It generates a detailed, day-by-day itinerary in HTML format, complete with descriptions and images of attractions.

## Features

*   **Automated Itinerary Generation:** Creates a full travel plan from simple inputs.
*   **Smart Transportation & Accommodation:** Suggests flights/trains and lodging that fit your budget.
*   **Intelligent Attraction Planning:** Discovers popular attractions, gathers detailed information, and organizes them into a logical daily schedule.
*   **Rich HTML Output:** Produces a visually appealing HTML file with images and descriptions for each point of interest.

## How to Use

1.  **Run the Agent Server:**
    ```bash
    mcp run -p 8000 multi_tool_agent.agent:app
    ```

2.  **Send a Request:**
    Make a POST request to the `/plan_trip` endpoint with your travel details.

    **Example using `curl`:**
    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/plan_trip' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "destination": "Paris",
      "duration_days": 5,
      "budget_usd": 2000
    }'
    ```

3.  **Get Your Plan:**
    The agent will process your request and save the generated itinerary as an HTML file (e.g., `trip_plan_for_Paris.html`) in the project directory.

## Technology Stack

*   **Google ADK:** The core framework for building the agent.
*   **FastAPI:** For creating the web server and API endpoints.
*   **Google Search & Maps Tools:** Used for finding transportation, accommodation, and points of interest.
*   **Firecrawl:** Used for scraping detailed information and images from the web.

