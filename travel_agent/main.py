"""
Travel AI Agent - Main Entry Point
Google ADK Integration for Intelligent Travel Planning
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
# from google.adk.agents import Agent  # Commented out due to YAML config issue
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to sys.path to enable absolute imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import with fallback for module path issues
try:
    from travel_agent.agents.travel_planner import TravelPlannerAgent
    from travel_agent.agents.data_collector import DataCollectorAgent
    from travel_agent.agents.report_generator import ReportGeneratorAgent
    from travel_agent.services.weather_service import WeatherService
    from travel_agent.utils.date_parser import parse_date, get_current_date_info
except ImportError:
    from agents.travel_planner import TravelPlannerAgent
    from agents.data_collector import DataCollectorAgent
    from agents.report_generator import ReportGeneratorAgent
    from services.weather_service import WeatherService
    from utils.date_parser import parse_date, get_current_date_info

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TravelAgent:
    """Main Travel AI Agent class that orchestrates the travel planning process."""
    
    def __init__(self, use_mcp_tool=None):
        """Initialize the Travel Agent with all sub-agents and optional MCP tool function."""
        # Pass MCP tool function to agents that need it
        self.use_mcp_tool = use_mcp_tool
        self.data_collector = DataCollectorAgent(use_mcp_tool=use_mcp_tool)
        self.travel_planner = TravelPlannerAgent()
        self.report_generator = ReportGeneratorAgent()
        
        # Initialize weather service with MCP tool parameter
        self.weather_service = WeatherService(use_mcp_tool=use_mcp_tool)
        
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        
        logger.info(f"Travel AI Agent initialized with MCP integration: {'enabled' if use_mcp_tool else 'disabled'}")
    
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
            logger.info(f"=== Starting travel planning for {destination} ===")
            logger.info(f"Parameters: destination={destination}, departure={departure_location}, start_date={start_date}, duration={duration}, budget={budget}")
            
            # Step 1: Collect destination data
            logger.info("Step 1: Collecting destination data...")
            travel_data = self.data_collector.collect_travel_data(
                destination=destination,
                departure_location=departure_location,
                start_date=start_date,
                duration=duration,
                budget=budget
            )
            
            logger.info(f"Data collection result: success={travel_data.get('success')}")
            if travel_data.get('success'):
                data_keys = list(travel_data.get('data', {}).keys())
                logger.info(f"Collected data keys: {data_keys}")
                # Log some sample data to verify collection
                if 'destination_info' in travel_data.get('data', {}):
                    dest_info = travel_data['data']['destination_info']
                    logger.info(f"Destination info sample: name={dest_info.get('name')}, description length={len(str(dest_info.get('description', '')))}")
            else:
                logger.error(f"Data collection failed: {travel_data.get('error')}")
                return {
                    'success': False,
                    'error': 'Failed to collect travel data',
                    'details': travel_data.get('error', 'Unknown error')
                }
            
            # Step 2: Generate travel plans
            logger.info("Step 2: Generating travel plans...")
            travel_plans = self.travel_planner.generate_plans(
                travel_data=travel_data['data'],
                preferences=preferences or {}
            )
            
            logger.info(f"Travel plans generation result: success={travel_plans.get('success')}")
            if travel_plans.get('success'):
                plans_count = len(travel_plans.get('plans', []))
                logger.info(f"Generated {plans_count} travel plans")
                for i, plan in enumerate(travel_plans.get('plans', [])):
                    logger.info(f"Plan {i+1}: type={plan.get('plan_type')}, budget={plan.get('total_budget')}")
            else:
                logger.error(f"Travel plans generation failed: {travel_plans.get('error')}")
                return {
                    'success': False,
                    'error': 'Failed to generate travel plans',
                    'details': travel_plans.get('error', 'Unknown error')
                }
            
            # Step 3: Generate HTML report
            logger.info("Step 3: Generating HTML report...")
            logger.info(f"Passing to report generator: destination={destination}, start_date={start_date}, duration={duration}, budget={budget}")
            
            report_result = self.report_generator.generate_html_report(
                travel_data=travel_data['data'],
                travel_plans=travel_plans['plans'],
                destination=destination,
                start_date=start_date,
                duration=duration,
                budget=budget
            )
            
            logger.info(f"HTML report generation result: success={report_result.get('success')}")
            if report_result.get('success'):
                logger.info(f"Travel plan generated successfully: {report_result['file_path']}")

                # Step 4: Generate Markdown report
                logger.info("Step 4: Generating Markdown report...")
                markdown_report_result = self.report_generator.generate_markdown_report(
                    report_data=report_result['report_data'],
                    destination=destination,
                    start_date=start_date
                )

                if markdown_report_result.get('success'):
                    logger.info(f"Markdown report generated successfully: {markdown_report_result['file_path']}")
                    report_result['markdown_file_path'] = markdown_report_result['file_path']
                else:
                    logger.error(f"Markdown report generation failed: {markdown_report_result.get('error')}")
                
                return {
                    'success': True,
                    'message': 'Travel plan generated successfully',
                    'file_path': report_result['file_path'],
                    'markdown_file_path': report_result.get('markdown_file_path'),
                    'plans_count': len(travel_plans['plans'])
                }
            else:
                logger.error(f"HTML report generation failed: {report_result.get('error')}")
                return {
                    'success': False,
                    'error': 'Failed to generate HTML report',
                    'details': report_result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"Error in travel planning: {str(e)}", exc_info=True)
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
    budget: float,
    use_mcp_tool=None
) -> Dict[str, Any]:
    """
    Tool function for Google ADK integration with intelligent date parsing and MCP support.
    
    Args:
        destination: Target destination
        departure_location: Starting location  
        start_date: Travel start date (can be relative like "后天" or absolute like "2025-07-28")
        duration: Number of travel days
        budget: Total budget
        use_mcp_tool: MCP tool function for external API calls
        
    Returns:
        Travel planning result
    """
    try:
        # Get current date information for logging
        current_info = get_current_date_info()
        logger.info(f"Current date info: {current_info}")
        logger.info(f"Received start_date parameter: '{start_date}'")
        
        # Parse the start_date to handle relative dates
        parsed_start_date = parse_date(start_date)
        logger.info(f"Parsed start_date: '{start_date}' -> '{parsed_start_date}'")
        
        # Log the planning request
        logger.info(f"Planning travel: {departure_location} -> {destination}")
        logger.info(f"Start date: {parsed_start_date} (original: {start_date})")
        logger.info(f"Duration: {duration} days, Budget: ¥{budget}")
        logger.info(f"MCP integration: {'enabled' if use_mcp_tool else 'disabled'}")
        
        # Create agent with MCP tool function and plan travel
        agent = TravelAgent(use_mcp_tool=use_mcp_tool)
        result = agent.plan_travel(
            destination=destination,
            departure_location=departure_location,
            start_date=parsed_start_date,  # Use parsed date
            duration=duration,
            budget=budget
        )
        
        # Add date parsing info to result
        if result.get('success'):
            result['date_parsing'] = {
                'original_date': start_date,
                'parsed_date': parsed_start_date,
                'current_date': current_info['current_date']
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Error in create_travel_planning_tool: {str(e)}")
        return {
            'success': False,
            'error': 'Error in travel planning tool',
            'details': str(e),
            'date_parsing_error': True
        }


# Google ADK Agent Configuration - Commented out due to YAML config issue
# travel_agent = Agent(
#     name="travel_planning_agent",
#     model="gemini-2.0-flash",
#     description=(
#         "Intelligent Travel Planning AI Agent that generates comprehensive, "
#         "illustrated travel itineraries based on destination, dates, duration, and budget."
#     ),
#     instruction=(
#         "You are an expert travel planning assistant. Generate detailed travel plans "
#         "that include attractions, accommodations, dining, transportation, and budget "
#         "optimization. Always provide multiple options (economic and comfort) and "
#         "create beautiful HTML reports with images and detailed information."
#     ),
#     tools=[create_travel_planning_tool],
# )


if __name__ == "__main__":
    # Example usage for testing
    agent = TravelAgent()
