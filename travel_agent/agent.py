# agent.py - Agent Development Kit主程序入口
import asyncio
from typing import Dict, List, Optional
from google.adk.agents import Agent
from pydantic import Field
from .modules.input_handler import InputHandler
from .modules.web_crawler import WebCrawler
from .modules.weather_service import WeatherService
from .modules.route_planner import RoutePlanner
from .modules.html_generator import HTMLGenerator

from google.adk.tools import google_search

class TravelPlanningAgent(Agent):
    """旅行规划AI Agent主类"""
    input_handler: InputHandler = Field(default_factory=InputHandler)
    web_crawler: Optional[WebCrawler] = None
    weather_service: WeatherService = Field(default_factory=WeatherService)
    route_planner: RoutePlanner = Field(default_factory=RoutePlanner)
    html_generator: HTMLGenerator = Field(default_factory=HTMLGenerator)

    def __init__(self, **kwargs):
        super().__init__(
            name="travel_planning_agent",
            description="A travel planning agent.",
            model="gemini-2.0-flash",
            tools=[google_search],
            **kwargs
        )
        self.web_crawler = WebCrawler()

    async def process_request(self, user_input: str) -> str:
        """处理用户旅行规划请求"""
        travel_info = self.input_handler.parse_input(user_input)
        attractions = self.web_crawler.get_attractions(travel_info["destination"])
        travel_plans = self.route_planner.plan_routes(travel_info, attractions)
        html_output = self.html_generator.generate_html(travel_plans, travel_info)
        with open(f"travel_plan.html", "w", encoding="utf-8") as f:
            f.write(html_output)
        return "I have created a travel plan for you. Please check the travel_plan.html file."

    def __call__(self, prompt: str) -> str:
        """
        This is the root agent for the travel agent application.
        It takes a prompt and returns a simple response.
        """
        return asyncio.run(self.process_request(prompt))

root_agent = TravelPlanningAgent()
