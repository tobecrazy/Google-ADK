"""
Travel AI Agent - Google ADK Integration
"""

from google.adk.agents import Agent
from .main import create_travel_planning_tool

root_agent = Agent(
    name="travel_planning_agent",
    model="gemini-2.0-flash",
    description=(
        "Intelligent Travel Planning AI Agent that generates comprehensive, "
        "illustrated travel itineraries based on destination, dates, duration, and budget."
    ),
    instruction=(
        "You are an expert travel planning assistant. Generate detailed travel plans "
        "that include attractions, accommodations, dining, transportation, and budget "
        "optimization. Always provide multiple options (economic and comfort) and "
        "create beautiful HTML reports with images and detailed information."
    ),
    tools=[create_travel_planning_tool],
)
