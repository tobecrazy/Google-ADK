# AI Travel Planner Agent

This agent helps you automatically plan your trip based on your destination, duration, and budget. It generates a detailed, day-by-day itinerary in HTML format, complete with descriptions and images of attractions.

## Features

*   **Automated Itinerary Generation:** Creates a full travel plan from simple inputs.
*   **Smart Transportation & Accommodation:** Suggests flights/trains and lodging that fit your budget.
*   **Intelligent Attraction Planning:** Discovers popular attractions, gathers detailed information, and organizes them into a logical daily schedule.
*   **Rich HTML Output:** Produces a visually appealing HTML file with images and descriptions for each point of interest.
*   **Input Validation:** Ensures valid input for departure date, travel days, budget, and plan type.
*   **In-memory Caching:** Caches Firecrawl search and scrape results to improve performance and reduce API calls for repeated requests.

## How to Use

1.  **Set up your Firecrawl API Key:**
    *   Obtain a Firecrawl API key from [https://firecrawl.dev/](https://firecrawl.dev/)
    *   Create a `.env` file in the `travel_agent` directory (i.e., `/Users/I321533/AI/Google-ADK/travel_agent/.env`) and add your Firecrawl API key:
        ```
        FIRECRAWL_API_KEY="YOUR_FIRECRAWL_API_KEY"
        ```

2.  **Install Dependencies:**
    ```bash
    cd /Users/I321533/AI/Google-ADK/travel_agent
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Run the Agent Server:**
    ```bash
    mcp run -p 8000 travel_agent.agent:app
    ```

4.  **Send a Request:**
    Make a POST request to the `/plan_trip` endpoint with your travel details.

    **Available `plan_type` options:** `economic`, `comfortable`, `luxury` (default: `comfortable`)

    **Example using `curl`:**
    ```bash
    curl -X 'POST' \
      'http://127.0.0.1:8000/plan_trip' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
      "departure_city": "Shanghai",
      "destination_city": "Paris",
      "departure_date": "2025-08-01",
      "travel_days": 5,
      "budget": 2000,
      "plan_type": "comfortable"
    }'
    ```

5.  **Get Your Plan:**
    The agent will process your request and save the generated itinerary as an HTML file (e.g., `trip_plan_for_Paris_comfortable.html`) in the project directory.

## Technology Stack

*   **Google ADK:** The core framework for building the agent.
*   **FastAPI:** For creating the web server and API endpoints.
*   **Firecrawl:** Used for web search and scraping detailed information and images from the web.
*   **Pydantic:** For data validation of input parameters.