# agent.py - Agent Development Kit主程序入口
import asyncio
from typing import Dict, List, Optional
from typing import Dict, List, Optional
from pydantic import Field
from .modules.input_handler import InputHandler
from .modules.web_crawler import WebCrawler
from .modules.weather_service import WeatherService
from .modules.route_planner import RoutePlanner
from .modules.html_generator import HTMLGenerator

from google.adk.agents import Agent
from huggingface_hub.inference._mcp.agent import Agent as HF_Agent
from huggingface_hub import InferenceClient
import datetime # Import datetime for default date

class TravelPlanningAgent(Agent):
    """旅行规划AI Agent主类"""
    input_handler: InputHandler = Field(default_factory=InputHandler)
    web_crawler: WebCrawler = Field(default_factory=WebCrawler)
    weather_service: WeatherService = Field(default_factory=WeatherService)
    route_planner: RoutePlanner = Field(default_factory=RoutePlanner)
    html_generator: HTMLGenerator = Field(default_factory=HTMLGenerator)
    client: Optional[InferenceClient] = None

    def __init__(self, model: str, **kwargs):
        super().__init__(
            name="travel_planning_agent",
            model=model,
            description="Travel planning AI Agent",
            instruction="You are a helpful agent that plans travel itineraries.",
            tools=[],
            **kwargs
        )
        self.client = InferenceClient(model=model) # Initialize InferenceClient

    
    async def generate_travel_plan_html(self, departure_city: str, destination: str, departure_date: str, duration: int, budget: int) -> str:
        """
        Generates a detailed HTML travel plan based on the provided travel information.
        Args:
            departure_city: The city of departure.
            destination: The travel destination.
            departure_date: The departure date in YYYY-MM-DD format.
            duration: The duration of the trip in days.
            budget: The budget for the trip.
        Returns:
            A message indicating that the HTML file has been created.
        """
        travel_info = {
            "departure_city": departure_city,
            "destination": destination,
            "departure_date": departure_date,
            "duration": duration,
            "budget": budget,
        }
        try:
            attractions = self.web_crawler.get_attractions(travel_info["destination"])
            travel_plans = self.route_planner.plan_routes(travel_info, attractions)
            html_output = self.html_generator.generate_html(travel_plans, travel_info)
            with open(f"travel_plan.html", "w", encoding="utf-8") as f:
                f.write(html_output)
            return "I have created a travel plan for you. Please check the travel_plan.html file."
        except Exception as e:
            return f"Error generating travel plan: {e}"

    async def process_request(self, user_input: str) -> str:
        """处理用户旅行规划请求"""
        # Parse the user input to extract travel information
        travel_info = self.input_handler.parse_input(user_input)

        # Manually construct the tool call
        tool_call_args = {
            "departure_city": travel_info.get("departure_city", ""),
            "destination": travel_info.get("destination", ""),
            "departure_date": travel_info.get("departure_date", str(datetime.date.today())),
            "duration": travel_info.get("duration", 1),
            "budget": travel_info.get("budget", 100),
        }
        
        # Call the tool directly
        return await self.generate_travel_plan_html(**tool_call_args)

    async def load_tools(self) -> None:
        # Register the generate_travel_plan_html tool
        await self.add_mcp_server(
            type="stdio",
            config={
                "command": "python",
                "args": ["-c", "from travel_agent.agent import TravelPlanningAgent; import asyncio; agent = TravelPlanningAgent(model='gemini-pro'); asyncio.run(agent.generate_travel_plan_html(**tool_call_args))"],
            },
        )

    async def load_tools(self) -> None:
        # Register the generate_travel_plan_html tool
        await self.add_mcp_server(
            type="stdio",
            config={
                "command": "python",
                "args": ["-c", "from travel_agent.agent import TravelPlanningAgent; import asyncio; agent = TravelPlanningAgent(model='gemini-pro'); asyncio.run(agent.generate_travel_plan_html(**tool_call_args))"],
            },
        )

    def __call__(self, prompt: str) -> str:
        """
        This is the root agent for the travel agent application.
        It takes a prompt and returns a simple response.
        """
        asyncio.run(self.load_tools())
        return asyncio.run(self.run(prompt))

root_agent = TravelPlanningAgent(model="gemini-1.5-flash")