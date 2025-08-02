"""
Data Collector Agent
Responsible for gathering travel-related data from various sources
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Add the parent directory to sys.path to enable absolute imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from travel_agent.services.weather_service_mcp import mcp_weather_service
from travel_agent.services.attraction_service import AttractionService
from travel_agent.services.transport_service import TransportService
from travel_agent.services.accommodation_service import AccommodationService
from travel_agent.services.restaurant_service import RestaurantService
from travel_agent.utils.web_scraper import WebScraper

logger = logging.getLogger(__name__)

class DataCollectorAgent:
    """Agent responsible for collecting comprehensive travel data."""
    
    def __init__(self, use_mcp_tool=None):
        """Initialize the data collector with all services and optional MCP tool function."""
        # Pass MCP tool function to services that need it
        self.use_mcp_tool = use_mcp_tool
        self.weather_service = mcp_weather_service
        self.attraction_service = AttractionService()
        self.transport_service = TransportService()
        self.accommodation_service = AccommodationService()
        self.restaurant_service = RestaurantService()
        self.web_scraper = WebScraper()
        
        # Initialize Gemini for intelligent data processing
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        logger.info(f"Data Collector Agent initialized with MCP integration: {'enabled' if use_mcp_tool else 'disabled'}")
    
    def collect_travel_data(
        self,
        destination: str,
        departure_location: str,
        start_date: str,
        duration: int,
        budget: float
    ) -> Dict[str, Any]:
        """
        Collect comprehensive travel data for the destination.
        
        Args:
            destination: Target destination
            departure_location: Starting location
            start_date: Travel start date
            duration: Number of days
            budget: Total budget
            
        Returns:
            Dict containing all collected travel data
        """
        try:
            logger.info(f"Collecting data for {destination}")
            
            # Parse dates
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = start_dt + timedelta(days=duration)
            
            # Collect data from all sources
            data = {
                'destination_info': self._get_destination_info(destination),
                'weather_data': self._get_weather_data(destination, start_date, duration),
                'attractions': self._get_attractions_data(destination, budget),
                'accommodations': self._get_accommodation_data(destination, start_date, duration, budget),
                'transportation': self._get_transport_data(departure_location, destination, start_date),
                'dining': self._get_dining_data(destination, budget),
                'local_info': self._get_local_info(destination),
                'budget_estimates': self._get_budget_estimates(destination, duration, budget)
            }
            
            # Validate and enrich data using AI
            enriched_data = self._enrich_data_with_ai(data, destination, duration, budget)
            
            return {
                'success': True,
                'data': enriched_data,
                'collection_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error collecting travel {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def _get_destination_info(self, destination: str) -> Dict[str, Any]:
        """Get basic destination information."""
        try:
            # Use AI to get comprehensive destination info
            prompt = f"""
            Provide comprehensive information about {destination} as a travel destination.
            Include:
            1. Brief description and highlights
            2. Best time to visit
            3. Local culture and customs
            4. Language and currency
            5. Time zone
            6. Key districts/areas to stay
            7. Transportation within city
            8. Safety tips
            
            Format as JSON with clear categories.
            """
            
            response = self.model.generate_content(prompt)
            
            # Basic fallback info
            basic_info = {
                'name': destination,
                'description': f"Popular travel destination: {destination}",
                'best_time_to_visit': 'Spring and Fall',
                'local_currency': 'Local Currency',
                'language': 'Local Language',
                'time_zone': 'Local Time Zone',
                'safety_rating': 'Generally Safe',
                'key_areas': ['City Center', 'Tourist District'],
                'local_transport': ['Public Transit', 'Taxi', 'Walking']
            }
            
            try:
                # Try to parse AI response as structured data
                ai_info = self._parse_ai_response(response.text)
                if ai_info:
                    basic_info.update(ai_info)
            except:
                pass
                
            return basic_info
            
        except Exception as e:
            logger.warning(f"Error getting destination info: {str(e)}")
            return {
                'name': destination,
                'description': f"Travel destination: {destination}",
                'error': str(e)
            }
    
    def _get_weather_data(self, destination: str, start_date: str, duration: int) -> Dict[str, Any]:
        """Get weather forecast for travel dates using MCP tools."""
        try:
            # First get the weather service response which indicates MCP is needed
            weather_response = self.weather_service.get_weather_forecast(destination, start_date, duration)
            
            # Check if MCP call is required
            if weather_response.get('mcp_required') and self.use_mcp_tool:
                logger.info(f"Making MCP weather call for {destination}")
                
                # Make the actual MCP call
                try:
                    mcp_response = self.use_mcp_tool(
                        server_name=weather_response['mcp_server'],
                        tool_name=weather_response['mcp_tool'],
                        arguments=weather_response['mcp_args']
                    )
                    
                    if mcp_response:
                        # Parse the MCP response using the weather service
                        parsed_weather = self.weather_service.parse_amap_weather_response(
                            mcp_response, start_date, duration
                        )
                        logger.info(f"Successfully got weather data from MCP for {destination}")
                        return parsed_weather
                    else:
                        logger.warning(f"Empty MCP response for weather data")
                        return weather_response  # Return original response with error info
                        
                except Exception as mcp_error:
                    logger.error(f"MCP weather call failed: {str(mcp_error)}")
                    return {
                        'success': False,
                        'destination': destination,
                        'error': f'MCP weather service error: {str(mcp_error)}',
                        'forecast': [],
                        'source': 'MCP Weather Service Error',
                        'note': '天气数据暂时无法获取，MCP服务连接失败。'
                    }
            else:
                # MCP not available, return the service response (which contains error info)
                logger.warning("MCP tool not available for weather service")
                return weather_response
                
        except Exception as e:
            logger.warning(f"Error getting weather data: {str(e)}")
            return {
                'success': False,
                'destination': destination,
                'forecast': [],
                'error': str(e),
                'source': 'Weather Service Error',
                'note': '天气数据获取失败，请手动查看天气预报。'
            }
    
    def _get_attractions_data(self, destination: str, budget: float) -> List[Dict[str, Any]]:
        """Get attractions and points of interest."""
        try:
            return self.attraction_service.get_attractions(destination, budget)
        except Exception as e:
            logger.warning(f"Error getting attractions data: {str(e)}")
            return []
    
    def _get_accommodation_data(self, destination: str, start_date: str, duration: int, budget: float) -> List[Dict[str, Any]]:
        """Get accommodation options."""
        try:
            return self.accommodation_service.get_accommodations(destination, start_date, duration, budget)
        except Exception as e:
            logger.warning(f"Error getting accommodation data: {str(e)}")
            return []
    
    def _get_transport_data(self, departure: str, destination: str, start_date: str) -> Dict[str, Any]:
        """Get transportation options."""
        try:
            return self.transport_service.get_transport_options(departure, destination, start_date)
        except Exception as e:
            logger.warning(f"Error getting transport data: {str(e)}")
            return {
                'options': [],
                'error': str(e)
            }
    
    def _get_dining_data(self, destination: str, budget: float) -> List[Dict[str, Any]]:
        """Get dining and restaurant recommendations using real data from Amap."""
        try:
            logger.info(f"Getting real restaurant data for {destination} with budget {budget}")
            
            # Use the new restaurant service to get real data from Amap
            restaurants = self.restaurant_service.get_restaurants(
                destination=destination,
                budget=budget
            )
            
            if restaurants and len(restaurants) > 0:
                logger.info(f"Successfully retrieved {len(restaurants)} real restaurants from Amap")
                return restaurants
            else:
                logger.warning("No restaurants found from Amap, falling back to AI-generated data")
                # Fallback to AI-generated data if Amap fails
                return self._get_ai_fallback_dining_data(destination, budget)
            
        except Exception as e:
            logger.error(f"Error getting real restaurant {str(e)}")
            # Fallback to AI-generated data
            return self._get_ai_fallback_dining_data(destination, budget)
    
    def _get_ai_fallback_dining_data(self, destination: str, budget: float) -> List[Dict[str, Any]]:
        """Get AI-generated dining data as fallback when real data fails."""
        try:
            logger.info(f"Using AI fallback for restaurant data in {destination}")
            
            # Use AI to generate dining recommendations
            prompt = f"""
            为{destination}推荐餐厅和当地美食，考虑不同预算水平：
            预算: {budget}元
            
            请提供8-10个餐厅推荐，包括：
            1. 当地特色菜和必尝美食
            2. 不同价位的餐厅（经济、中档、高端）
            3. 街头小吃选择
            4. 素食等特殊饮食需求
            5. 预估用餐费用
            
            请用中文回答，提供多样化的选择。
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse and structure the response
            dining_data = self._parse_dining_recommendations(response.text, budget)
            
            # Add fallback indicator
            for restaurant in dining_data:
                restaurant['data_source'] = 'ai_fallback'
                restaurant['note'] = '基于AI生成的推荐，建议出行前核实具体信息'
            
            return dining_data
            
        except Exception as e:
            logger.error(f"Error getting AI fallback dining data: {str(e)}")
            return []
    
    def _get_local_info(self, destination: str) -> Dict[str, Any]:
        """Get local information and tips."""
        try:
            prompt = f"""
            Provide practical local information for travelers to {destination}:
            1. Tipping customs
            2. Local etiquette and customs
            3. Emergency contacts
            4. Common phrases in local language
            5. Shopping areas and markets
            6. Local SIM card/WiFi options
            7. Public restroom locations
            8. Cultural events or festivals
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                'practical_tips': response.text,
                'emergency_numbers': ['Police: Local Number', 'Medical: Local Number'],
                'useful_phrases': ['Hello', 'Thank you', 'Excuse me', 'How much?'],
                'shopping_areas': ['Main Shopping District', 'Local Markets'],
                'cultural_notes': 'Respect local customs and traditions'
            }
            
        except Exception as e:
            logger.warning(f"Error getting local info: {str(e)}")
            return {
                'practical_tips': f"General travel tips for {destination}",
                'error': str(e)
            }
    
    def _get_budget_estimates(self, destination: str, duration: int, budget: float) -> Dict[str, Any]:
        """Get budget estimates for different categories."""
        try:
            # Calculate budget allocation
            transport_budget = budget * 0.30
            accommodation_budget = budget * 0.35
            dining_budget = budget * 0.20
            activities_budget = budget * 0.15
            
            return {
                'total_budget': budget,
                'daily_budget': budget / duration,
                'categories': {
                    'transportation': {
                        'budget': transport_budget,
                        'percentage': 30,
                        'daily': transport_budget / duration
                    },
                    'accommodation': {
                        'budget': accommodation_budget,
                        'percentage': 35,
                        'daily': accommodation_budget / duration
                    },
                    'dining': {
                        'budget': dining_budget,
                        'percentage': 20,
                        'daily': dining_budget / duration
                    },
                    'activities': {
                        'budget': activities_budget,
                        'percentage': 15,
                        'daily': activities_budget / duration
                    }
                }
            }
            
        except Exception as e:
            logger.warning(f"Error calculating budget estimates: {str(e)}")
            return {
                'total_budget': budget,
                'error': str(e)
            }
    
    def _enrich_data_with_ai(self, data: Dict[str, Any], destination: str, duration: int, budget: float) -> Dict[str, Any]:
        """Use AI to enrich and validate collected data."""
        try:
            # Add AI-generated insights and recommendations
            prompt = f"""
            Based on the travel data for {destination} (duration: {duration} days, budget: {budget}),
            provide additional insights and recommendations:
            
            1. Hidden gems and off-the-beaten-path attractions
            2. Seasonal considerations and what to pack
            3. Money-saving tips specific to this destination
            4. Cultural experiences not to miss
            5. Day trip options from the main destination
            6. Photography spots and Instagram-worthy locations
            7. Local transportation hacks
            8. Booking timing recommendations
            """
            
            response = self.model.generate_content(prompt)
            
            data['ai_insights'] = {
                'recommendations': response.text,
                'generated_at': datetime.now().isoformat()
            }
            
            return data
            
        except Exception as e:
            logger.warning(f"Error enriching data with AI: {str(e)}")
            return data
    
    def _parse_ai_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse AI response into structured data."""
        try:
            # Simple parsing logic - can be enhanced
            lines = response_text.split('\n')
            parsed_data = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    parsed_data[key.strip().lower().replace(' ', '_')] = value.strip()
            
            return parsed_data if parsed_data else None
            
        except Exception as e:
            logger.warning(f"Error parsing AI response: {str(e)}")
            return None
    
    def _parse_dining_recommendations(self, response_text: str, budget: float) -> List[Dict[str, Any]]:
        """Parse dining recommendations from AI response."""
        try:
            # Generate AI-based dining recommendations for the specific destination
            daily_food_budget = (budget * 0.20) / 7  # Assuming 7 days average
            
            # Use AI to parse the response and extract restaurant information
            restaurants = self._extract_restaurant_info(response_text, daily_food_budget)
            
            # If AI parsing fails or returns no restaurants, generate fallback restaurants
            if not restaurants:
                restaurants = self._generate_fallback_restaurants(daily_food_budget)
            
            return restaurants
            
        except Exception as e:
            logger.warning(f"Error parsing dining recommendations: {str(e)}")
            # Return fallback restaurants in case of error
            try:
                daily_food_budget = (budget * 0.20) / 7
                return self._generate_fallback_restaurants(daily_food_budget)
            except:
                return []

    
    def _extract_restaurant_info(self, ai_response: str, daily_budget: float) -> List[Dict[str, Any]]:
        """Extract restaurant information from AI response."""
        try:
            import re
            import json
            
            restaurants = []
            
            # Try to parse as JSON first
            try:
                data = json.loads(ai_response)
                if isinstance(data, list):
                    restaurants = data[:8]  # Limit to 8 restaurants
                    # Validate and enhance restaurant data
                    for restaurant in restaurants:
                        self._validate_and_enhance_restaurant(restaurant, daily_budget)
                    return restaurants
            except json.JSONDecodeError:
                pass
            
            # If JSON parsing fails, try to extract from text using regex
            # Look for restaurant sections
            restaurant_patterns = [
                r'(?:餐厅|餐馆|美食|餐饮).*?(?=(?:餐厅|餐馆|美食|餐饮)|$)',
                r'(?:Restaurant|Dining|Food|Cuisine).*?(?=(?:Restaurant|Dining|Food|Cuisine)|$)'
            ]
            
            for pattern in restaurant_patterns:
                matches = re.findall(pattern, ai_response, re.DOTALL | re.IGNORECASE)
                if matches and len(matches) > 0:
                    for match in matches[:8]:  # Limit to 8 restaurants
                        restaurant = self._parse_restaurant_from_text(match, daily_budget)
                        if restaurant:
                            restaurants.append(restaurant)
                    if restaurants:
                        break
            
            # If still no restaurants found, create basic structure from response
            if not restaurants:
                # Split response into lines and look for restaurant-like entries
                lines = ai_response.split('\n')
                for i, line in enumerate(lines):
                    line = line.strip()
                    if line and len(line) > 10 and i < 8:  # Only consider substantial lines, limit to 8
                        restaurants.append({
                            'name': line[:30],  # First 30 chars as name
                            'cuisine': 'Local',
                            'price_range': self._estimate_price_range(daily_budget),
                            'estimated_cost': daily_budget * 0.7,
                            'specialties': ['当地特色菜'],
                            'rating': 4.0,
                            'location': '当地区域'
                        })
            
            return restaurants[:8]  # Return up to 8 restaurants
            
        except Exception as e:
            logger.warning(f"Error extracting restaurant info: {str(e)}")
            return []
    
    def _parse_restaurant_from_text(self, text: str, daily_budget: float) -> Dict[str, Any]:
        """Parse restaurant information from text."""
        try:
            import re
            
            # Clean the text
            text = re.sub(r'[^\w\s\u4e00-\u9fff.,:;!?-]', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Extract name (first substantial phrase)
            name_match = re.search(r'^([^\n]{5,30}?)(?:\s|$)', text)
            name = name_match.group(1).strip() if name_match else "当地餐厅"
            
            # Extract cuisine keywords
            cuisine_keywords = ['中餐', '西餐', '日料', '韩餐', '东南亚菜', '快餐', '小吃', '素食']
            cuisine = 'Local'
            for keyword in cuisine_keywords:
                if keyword in text:
                    cuisine = keyword
                    break
            
            # Extract price range indicators
            price_range = self._estimate_price_range(daily_budget)
            
            # Extract specialties (look for food items)
            specialties = []
            food_patterns = [
                r'推荐(?:菜品|美食|菜式)[:,：]?\s*([^。\n]+)',
                r'特色(?:菜品|美食|菜式)[:,：]?\s*([^。\n]+)',
                r'(?:必点|必尝|招牌)[^:：]*[:,：]?\s*([^。\n]+)'
            ]
            
            for pattern in food_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    special_items = match.group(1).split('、')
                    specialties.extend([item.strip() for item in special_items if item.strip()])
                    break
            
            if not specialties:
                specialties = ['当地特色菜']
            
            # Create restaurant object
            restaurant = {
                'name': name[:30],  # Limit name length
                'cuisine': cuisine,
                'price_range': price_range,
                'estimated_cost': daily_budget * (0.5 + hash(name) % 100 / 200),  # Randomize cost
                'specialties': specialties[:5],  # Limit to 5 specialties
                'rating': 4.0 + (hash(name) % 20) / 10,  # Randomize rating between 4.0-5.0
                'location': '当地区域'
            }
            
            return restaurant
            
        except Exception as e:
            logger.warning(f"Error parsing restaurant from text: {str(e)}")
            return None
    
    def _estimate_price_range(self, budget: float) -> str:
        """Estimate price range based on budget."""
        if budget < 50:
            return 'Budget'
        elif budget < 150:
            return 'Mid-range'
        else:
            return 'High-end'
    
    def _validate_and_enhance_restaurant(self, restaurant: Dict[str, Any], daily_budget: float) -> Dict[str, Any]:
        """Validate and enhance restaurant data."""
        try:
            # Ensure required fields exist
            required_fields = {
                'name': '当地餐厅',
                'cuisine': 'Local',
                'price_range': self._estimate_price_range(daily_budget),
                'estimated_cost': daily_budget,
                'specialties': ['当地特色菜'],
                'rating': 4.0,
                'location': '当地区域'
            }
            
            for field, default_value in required_fields.items():
                if field not in restaurant or not restaurant[field]:
                    restaurant[field] = default_value
            
            # Validate data types
            if not isinstance(restaurant.get('name'), str):
                restaurant['name'] = str(restaurant.get('name', '当地餐厅'))
            
            if not isinstance(restaurant.get('estimated_cost'), (int, float)):
                restaurant['estimated_cost'] = daily_budget
            
            if not isinstance(restaurant.get('rating'), (int, float)):
                restaurant['rating'] = 4.0
            
            if not isinstance(restaurant.get('specialties'), list):
                restaurant['specialties'] = ['当地特色菜']
            
            # Ensure name is not too long
            if len(str(restaurant.get('name', ''))) > 50:
                restaurant['name'] = str(restaurant['name'])[:50]
            
            # Ensure specialties list is reasonable
            if len(restaurant.get('specialties', [])) > 10:
                restaurant['specialties'] = restaurant['specialties'][:10]
            
            return restaurant
            
        except Exception as e:
            logger.warning(f"Error validating restaurant: {str(e)}")
            return restaurant
    
    def _generate_fallback_restaurants(self, daily_budget: float) -> List[Dict[str, Any]]:
        """Generate fallback restaurants when AI parsing fails."""
        try:
            # If AI fails, create generic fallback restaurants
            fallback_restaurants = [
                {
                    'name': '当地老字号餐厅',
                    'cuisine': 'Local Traditional',
                    'price_range': 'Mid-range',
                    'estimated_cost': daily_budget * 0.8,
                    'specialties': ['传统地方菜', '招牌菜1', '招牌菜2'],
                    'rating': 4.3,
                    'location': '老城区'
                },
                {
                    'name': '街头小吃摊',
                    'cuisine': 'Street Food',
                    'price_range': 'Budget',
                    'estimated_cost': daily_budget * 0.3,
                    'specialties': ['当地小吃1', '当地小吃2', '特色小食'],
                    'rating': 4.1,
                    'location': '夜市'
                },
                {
                    'name': '精品餐厅',
                    'cuisine': 'Local Gourmet',
                    'price_range': 'High-end',
                    'estimated_cost': daily_budget * 1.5,
                    'specialties': ['创意菜品', '精致料理', '特色套餐'],
                    'rating': 4.6,
                    'location': '商业区'
                }
            ]
            
            return fallback_restaurants
            
        except Exception as e:
            logger.error(f"Error generating fallback restaurants: {str(e)}")
            return []
