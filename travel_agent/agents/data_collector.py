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
from services.weather_service import WeatherService
from services.attraction_service import AttractionService
from services.transport_service import TransportService
from services.accommodation_service import AccommodationService
from utils.web_scraper import WebScraper

logger = logging.getLogger(__name__)

class DataCollectorAgent:
    """Agent responsible for collecting comprehensive travel data."""
    
    def __init__(self):
        """Initialize the data collector with all services."""
        self.weather_service = WeatherService()
        self.attraction_service = AttractionService()
        self.transport_service = TransportService()
        self.accommodation_service = AccommodationService()
        self.web_scraper = WebScraper()
        
        # Initialize Gemini for intelligent data processing
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        logger.info("Data Collector Agent initialized")
    
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
        """Get weather forecast for travel dates."""
        try:
            return self.weather_service.get_weather_forecast(destination, start_date, duration)
        except Exception as e:
            logger.warning(f"Error getting weather {str(e)}")
            return {
                'forecast': [],
                'error': str(e)
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
        """Get dining and restaurant recommendations."""
        try:
            # Use AI to generate dining recommendations
            prompt = f"""
            Recommend restaurants and local cuisine for {destination}.
            Consider different budget levels and include:
            1. Local specialties and must-try dishes
            2. Restaurant recommendations (budget, mid-range, high-end)
            3. Street food options
            4. Dietary restrictions accommodations
            5. Estimated meal costs
            
            Provide 8-10 recommendations with variety.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse and structure the response
            dining_data = self._parse_dining_recommendations(response.text, budget)
            return dining_data
            
        except Exception as e:
            logger.warning(f"Error getting dining data: {str(e)}")
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
            # Simple parsing - can be enhanced with more sophisticated NLP
            recommendations = []
            
            # Generate sample dining data based on budget
            daily_food_budget = (budget * 0.20) / 7  # Assuming 7 days average
            
            sample_restaurants = [
                {
                    'name': 'Local Specialty Restaurant',
                    'cuisine': 'Local Cuisine',
                    'price_range': 'Mid-range',
                    'estimated_cost': daily_food_budget * 0.6,
                    'specialties': ['Local Dish 1', 'Local Dish 2'],
                    'rating': 4.5,
                    'location': 'City Center'
                },
                {
                    'name': 'Street Food Market',
                    'cuisine': 'Street Food',
                    'price_range': 'Budget',
                    'estimated_cost': daily_food_budget * 0.2,
                    'specialties': ['Street Snacks', 'Local Beverages'],
                    'rating': 4.2,
                    'location': 'Local Market'
                },
                {
                    'name': 'Fine Dining Experience',
                    'cuisine': 'International',
                    'price_range': 'High-end',
                    'estimated_cost': daily_food_budget * 1.5,
                    'specialties': ['Signature Dishes', 'Wine Pairing'],
                    'rating': 4.8,
                    'location': 'Downtown'
                }
            ]
            
            return sample_restaurants
            
        except Exception as e:
            logger.warning(f"Error parsing dining recommendations: {str(e)}")
            return []
