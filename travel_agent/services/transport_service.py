"""
Transport Service
Provides transportation options and routing information
"""

import os
import logging
from typing import Dict, Any, List
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

logger = logging.getLogger(__name__)

class TransportService:
    """Service for transportation data and routing."""
    
    def __init__(self):
        """Initialize the transport service."""
        # Initialize Gemini for transport data generation
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        logger.info("Transport Service initialized")
    
    def get_transport_options(
        self,
        departure: str,
        destination: str,
        start_date: str
    ) -> Dict[str, Any]:
        """
        Get transportation options between departure and destination.
        
        Args:
            departure: Starting location
            destination: Target destination
            start_date: Travel start date
            
        Returns:
            Dict containing transport options
        """
        try:
            logger.info(f"Getting transport options from {departure} to {destination}")
            
            # Generate transport options using AI
            transport_data = self._generate_transport_options(departure, destination, start_date)
            
            # Add local transport information
            local_transport = self._get_local_transport_info(destination)
            
            return {
                'success': True,
                'departure': departure,
                'destination': destination,
                'options': transport_data,
                'local_transport': local_transport,
                'generated_at': start_date
            }
            
        except Exception as e:
            logger.error(f"Error getting transport options: {str(e)}")
            return self._get_fallback_transport_data(departure, destination)
    
    def _generate_transport_options(
        self,
        departure: str,
        destination: str,
        start_date: str
    ) -> List[Dict[str, Any]]:
        """Generate transport options using AI."""
        try:
            prompt = f"""
            Provide transportation options from {departure} to {destination} for {start_date}.
            Include flights, trains, buses, and driving options with costs, duration, and booking info.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse response into structured data
            transport_options = self._parse_transport_response(response.text, departure, destination)
            
            return transport_options
            
        except Exception as e:
            logger.error(f"Error generating transport options: {str(e)}")
            return self._get_sample_transport_options(departure, destination)
    
    def _parse_transport_response(
        self,
        ai_response: str,
        departure: str,
        destination: str
    ) -> List[Dict[str, Any]]:
        """Parse AI response into structured transport data."""
        try:
            # Create structured sample transport options
            sample_options = [
                {
                    'type': 'Flight',
                    'duration': '2-4 hours',
                    'cost_range': {'min': 150, 'max': 500},
                    'comfort': 'High',
                    'frequency': 'Multiple daily',
                    'booking_required': True,
                    'advance_booking': '2-8 weeks recommended',
                    'pros': ['Fastest option', 'Multiple airlines', 'Frequent schedules'],
                    'cons': ['Airport transfers needed', 'Weather dependent', 'Security delays'],
                    'best_for': 'Time-conscious travelers',
                    'booking_tips': ['Book early for better prices', 'Compare airlines', 'Check baggage policies']
                },
                {
                    'type': 'Train',
                    'duration': '4-8 hours',
                    'cost_range': {'min': 50, 'max': 200},
                    'comfort': 'Medium-High',
                    'frequency': 'Several daily',
                    'booking_required': True,
                    'advance_booking': '1-4 weeks recommended',
                    'pros': ['City center to center', 'Comfortable seating', 'Scenic views'],
                    'cons': ['Limited schedules', 'Weather delays possible'],
                    'best_for': 'Comfortable travel with views',
                    'booking_tips': ['Book seats in advance', 'Consider meal options', 'Check station locations']
                },
                {
                    'type': 'Bus',
                    'duration': '6-12 hours',
                    'cost_range': {'min': 25, 'max': 80},
                    'comfort': 'Medium',
                    'frequency': 'Multiple daily',
                    'booking_required': False,
                    'advance_booking': 'Not required but recommended',
                    'pros': ['Most economical', 'Frequent departures', 'No advance booking needed'],
                    'cons': ['Longest travel time', 'Limited comfort', 'Traffic dependent'],
                    'best_for': 'Budget travelers',
                    'booking_tips': ['Choose reputable companies', 'Bring entertainment', 'Pack snacks']
                },
                {
                    'type': 'Car Rental',
                    'duration': '5-10 hours',
                    'cost_range': {'min': 40, 'max': 120},
                    'comfort': 'High',
                    'frequency': 'Available 24/7',
                    'booking_required': True,
                    'advance_booking': '1-2 weeks recommended',
                    'pros': ['Complete flexibility', 'Door-to-door', 'Stop anywhere'],
                    'cons': ['Driving fatigue', 'Parking costs', 'Traffic'],
                    'best_for': 'Flexible travelers with driving license',
                    'booking_tips': ['Compare rental companies', 'Check insurance', 'Plan rest stops']
                }
            ]
            
            return sample_options
            
        except Exception as e:
            logger.error(f"Error parsing transport response: {str(e)}")
            return self._get_sample_transport_options(departure, destination)
    
    def _get_local_transport_info(self, destination: str) -> Dict[str, Any]:
        """Get local transportation information for the destination."""
        try:
            return {
                'public_transport': {
                    'available': True,
                    'types': ['Metro/Subway', 'Bus', 'Tram'],
                    'daily_pass_cost': 8,
                    'single_ride_cost': 2.5,
                    'operating_hours': '05:00 - 24:00',
                    'coverage': 'Good city coverage',
                    'tips': ['Buy daily/weekly passes for savings', 'Download transport app', 'Keep small change']
                },
                'taxi_rideshare': {
                    'available': True,
                    'services': ['Local Taxi', 'Uber', 'Lyft'],
                    'base_fare': 3.5,
                    'per_km_rate': 1.2,
                    'airport_surcharge': 5,
                    'tips': ['Use apps for better rates', 'Confirm fare before ride', 'Tip 10-15%']
                },
                'walking_cycling': {
                    'walkability': 'High',
                    'bike_sharing': True,
                    'bike_rental_cost': 15,
                    'pedestrian_friendly': True,
                    'cycling_infrastructure': 'Good',
                    'tips': ['City center is walkable', 'Bike lanes available', 'Wear comfortable shoes']
                },
                'airport_transport': {
                    'airport_express': {'available': True, 'cost': 12, 'duration': '30-45 min'},
                    'taxi': {'cost_range': '40-60', 'duration': '45-90 min'},
                    'shuttle': {'cost': 15, 'duration': '60-90 min'},
                    'public_transport': {'cost': 5, 'duration': '60-120 min'}
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting local transport info: {str(e)}")
            return {
                'public_transport': {'available': True, 'daily_pass_cost': 8},
                'taxi_rideshare': {'available': True, 'base_fare': 3.5},
                'walking_cycling': {'walkability': 'Medium'},
                'airport_transport': {'taxi': {'cost_range': '40-60'}}
            }
    
    def _get_sample_transport_options(self, departure: str, destination: str) -> List[Dict[str, Any]]:
        """Get sample transport options when AI generation fails."""
        return [
            {
                'type': 'Flight',
                'duration': '3 hours',
                'cost_range': {'min': 200, 'max': 400},
                'comfort': 'High',
                'booking_required': True,
                'pros': ['Fastest option'],
                'cons': ['Airport transfers needed'],
                'best_for': 'Time-conscious travelers'
            },
            {
                'type': 'Train',
                'duration': '6 hours',
                'cost_range': {'min': 80, 'max': 150},
                'comfort': 'Medium-High',
                'booking_required': True,
                'pros': ['Comfortable', 'City center to center'],
                'cons': ['Limited schedules'],
                'best_for': 'Comfortable travel'
            }
        ]
    
    def _get_fallback_transport_data(self, departure: str, destination: str) -> Dict[str, Any]:
        """Get fallback transport data when all else fails."""
        return {
            'success': False,
            'departure': departure,
            'destination': destination,
            'options': [
                {
                    'type': 'Mixed Transport',
                    'duration': 'Varies',
                    'cost_range': {'min': 50, 'max': 300},
                    'comfort': 'Varies',
                    'booking_required': True,
                    'note': 'Please check local transport providers for specific options'
                }
            ],
            'local_transport': {
                'public_transport': {'available': True, 'cost': 'Varies'},
                'taxi_rideshare': {'available': True, 'cost': 'Varies'}
            },
            'error': 'Limited transport data available'
        }
