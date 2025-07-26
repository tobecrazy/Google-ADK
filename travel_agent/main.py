"""
Travel AI Agent - Main Entry Point
Google ADK Integration for Intelligent Travel Planning
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from google.adk.agents import Agent
from agents.travel_planner import TravelPlannerAgent
from agents.data_collector import DataCollectorAgent
from agents.report_generator import ReportGeneratorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TravelAgent:
    """Main Travel AI Agent class that orchestrates the travel planning process."""
    
    def __init__(self):
        """Initialize the Travel Agent with all sub-agents."""
        self.data_collector = DataCollectorAgent()
        self.travel_planner = TravelPlannerAgent()
        self.report_generator = ReportGeneratorAgent()
        
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        
        logger.info("Travel AI Agent initialized successfully")
    
    def plan_travel(
        self,
        destination: str,
        departure_location: str,
        start_date: str,
        duration: int,
        budget: float,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive travel plan.
        
        Args:
            destination: Target destination city/country
            departure_location: Starting location
            start_date: Travel start date (YYYY-MM-DD)
            duration: Number of travel days
            budget: Total budget in local currency
            preferences: Optional user preferences
            
        Returns:
            Dict containing plan status and output file path
        """
        try:
            logger.info(f"Starting travel planning for {destination}")
            
            # Step 1: Collect destination data
            logger.info("Collecting destination data...")
            travel_data = self.data_collector.collect_travel_data(
                destination=destination,
                departure_location=departure_location,
                start_date=start_date,
                duration=duration,
                budget=budget
            )
            
            if not travel_data.get('success'):
                return {
                    'success': False,
                    'error': 'Failed to collect travel data',
                    'details': travel_data.get('error', 'Unknown error')
                }
            
            # Step 2: Generate travel plans
            logger.info("Generating travel plans...")
            travel_plans = self.travel_planner.generate_plans(
                travel_data=travel_data['data'],
                preferences=preferences or {}
            )
            
            if not travel_plans.get('success'):
                return {
                    'success': False,
                    'error': 'Failed to generate travel plans',
                    'details': travel_plans.get('error', 'Unknown error')
                }
            
            # Step 3: Generate HTML report
            logger.info("Generating HTML report...")
            report_result = self.report_generator.generate_html_report(
                travel_data=travel_data['data'],
                travel_plans=travel_plans['plans'],
                destination=destination,
                start_date=start_date,
                duration=duration,
                budget=budget
            )
            
            if report_result.get('success'):
                logger.info(f"Travel plan generated successfully: {report_result['file_path']}")
                return {
                    'success': True,
                    'message': 'Travel plan generated successfully',
                    'file_path': report_result['file_path'],
                    'plans_count': len(travel_plans['plans'])
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to generate HTML report',
                    'details': report_result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"Error in travel planning: {str(e)}")
            return {
                'success': False,
                'error': 'Unexpected error occurred',
                'details': str(e)
            }


def create_travel_planning_tool(
    destination: str,
    departure_location: str,
    start_date: str,
    duration: int,
    budget: float
) -> Dict[str, Any]:
    """
    Tool function for Google ADK integration.
    
    Args:
        destination: Target destination
        departure_location: Starting location  
        start_date: Travel start date (YYYY-MM-DD)
        duration: Number of travel days
        budget: Total budget
        
    Returns:
        Travel planning result
    """
    agent = TravelAgent()
    return agent.plan_travel(
        destination=destination,
        departure_location=departure_location,
        start_date=start_date,
        duration=duration,
        budget=budget
    )


# Google ADK Agent Configuration
travel_agent = Agent(
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


if __name__ == "__main__":
    # Example usage for testing
    agent = TravelAgent()
    
    result = agent.plan_travel(
        destination="Tokyo, Japan",
        departure_location="Shanghai, China",
        start_date="2024-04-01",
        duration=7,
        budget=10000
    )
    
    print(f"Planning result: {result}")
