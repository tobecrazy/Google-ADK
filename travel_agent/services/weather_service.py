"""
Weather Service
Integrates with weather APIs to provide forecast data
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import requests
from pypinyin import pinyin, Style
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

logger = logging.getLogger(__name__)

class WeatherService:
    """Service for weather data integration."""
    
    def __init__(self):
        """Initialize the weather service."""
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        if not self.api_key:
            logger.warning("OpenWeather API key not found. Weather service will use mock data.")
        
        logger.info("Weather Service initialized")
    
    def get_weather_forecast(
        self,
        destination: str,
        start_date: str,
        duration: int
    ) -> Dict[str, Any]:
        """
        Get weather forecast for travel dates.
        
        Args:
            destination: Destination city
            start_date: Start date (YYYY-MM-DD)
            duration: Number of days
            
        Returns:
            Dict containing weather forecast data
        """
        try:
            if not self.api_key:
                return self._get_mock_weather_data(destination, start_date, duration)
            
            # Convert Chinese city names to Pinyin
            city_query = self._convert_city_name(destination)
            
            # Get current weather first to validate city
            current_weather = self._get_current_weather(city_query)
            if not current_weather.get('success'):
                logger.warning(f"Could not get weather for {destination}, using mock data")
                return self._get_mock_weather_data(destination, start_date, duration)
            
            # Get forecast data
            forecast_data = self._get_forecast_data(city_query, start_date, duration)
            
            return {
                'success': True,
                'destination': destination,
                'current_weather': current_weather.get('data', {}),
                'forecast': forecast_data,
                'source': 'OpenWeatherMap'
            }
            
        except Exception as e:
            logger.error(f"Error getting weather forecast: {str(e)}")
            return self._get_mock_weather_data(destination, start_date, duration)
    
    def _convert_city_name(self, city: str) -> str:
        """Convert Chinese city names to Pinyin."""
        try:
            if any('\u4e00' <= char <= '\u9fff' for char in city):
                pinyin_parts = pinyin(city, style=Style.NORMAL)
                return "".join([part[0].capitalize() for part in pinyin_parts])
            return city
        except Exception as e:
            logger.warning(f"Error converting city name: {str(e)}")
            return city
    
    def _get_current_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather for city validation."""
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'en'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('cod') == 200:
                weather_data = {
                    'temperature': data['main']['temp'],
                    'condition': data['weather'][0]['description'].title(),
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed'],
                    'pressure': data['main']['pressure']
                }
                
                return {
                    'success': True,
                    'data': weather_data
                }
            else:
                return {
                    'success': False,
                    'error': data.get('message', 'Unknown error')
                }
                
        except Exception as e:
            logger.error(f"Error getting current weather: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_forecast_data(self, city: str, start_date: str, duration: int) -> List[Dict[str, Any]]:
        """Get forecast data for the travel period."""
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'en'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('cod') == '200':
                return self._process_forecast_data(data, start_date, duration)
            else:
                logger.warning(f"Forecast API error: {data.get('message', 'Unknown error')}")
                return self._generate_mock_forecast(start_date, duration)
                
        except Exception as e:
            logger.error(f"Error getting forecast {str(e)}")
            return self._generate_mock_forecast(start_date, duration)
    
    def _process_forecast_data(self, data: Dict[str, Any], start_date: str, duration: int) -> List[Dict[str, Any]]:
        """Process raw forecast data into structured format."""
        try:
            forecast_list = []
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            
            # Group forecasts by date
            daily_forecasts = {}
            
            for item in data.get('list', []):
                forecast_dt = datetime.fromtimestamp(item['dt'])
                date_key = forecast_dt.strftime('%Y-%m-%d')
                
                if date_key not in daily_forecasts:
                    daily_forecasts[date_key] = []
                
                daily_forecasts[date_key].append({
                    'time': forecast_dt.strftime('%H:%M'),
                    'temperature': item['main']['temp'],
                    'condition': item['weather'][0]['description'].title(),
                    'humidity': item['main']['humidity'],
                    'wind_speed': item['wind']['speed'],
                    'precipitation': item.get('rain', {}).get('3h', 0) + item.get('snow', {}).get('3h', 0)
                })
            
            # Create daily summaries
            for i in range(duration):
                current_date = start_dt + timedelta(days=i)
                date_str = current_date.strftime('%Y-%m-%d')
                
                if date_str in daily_forecasts:
                    day_data = daily_forecasts[date_str]
                    
                    # Calculate daily averages
                    avg_temp = sum(item['temperature'] for item in day_data) / len(day_data)
                    avg_humidity = sum(item['humidity'] for item in day_data) / len(day_data)
                    total_precipitation = sum(item['precipitation'] for item in day_data)
                    
                    # Get most common condition
                    conditions = [item['condition'] for item in day_data]
                    most_common_condition = max(set(conditions), key=conditions.count)
                    
                    forecast_list.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'day_name': current_date.strftime('%A'),
                        'temperature': round(avg_temp, 1),
                        'condition': most_common_condition,
                        'humidity': round(avg_humidity),
                        'precipitation': round(total_precipitation, 1),
                        'hourly_details': day_data[:8]  # First 8 hourly forecasts
                    })
                else:
                    # Generate mock data for dates not covered by API
                    forecast_list.append(self._generate_mock_day_forecast(current_date))
            
            return forecast_list
            
        except Exception as e:
            logger.error(f"Error processing forecast {str(e)}")
            return self._generate_mock_forecast(start_date, duration)
    
    def _generate_mock_forecast(self, start_date: str, duration: int) -> List[Dict[str, Any]]:
        """Generate mock forecast data when API is unavailable."""
        try:
            forecast_list = []
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            
            # Mock weather conditions
            conditions = ['Sunny', 'Partly Cloudy', 'Cloudy', 'Light Rain', 'Clear']
            base_temp = 22  # Base temperature in Celsius
            
            for i in range(duration):
                current_date = start_dt + timedelta(days=i)
                
                # Vary temperature slightly
                temp_variation = (i % 5) - 2  # -2 to +2 degrees variation
                temperature = base_temp + temp_variation
                
                forecast_list.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'day_name': current_date.strftime('%A'),
                    'temperature': temperature,
                    'condition': conditions[i % len(conditions)],
                    'humidity': 60 + (i % 20),  # 60-80% humidity
                    'precipitation': 0.1 if i % 3 == 0 else 0,  # Occasional light rain
                    'hourly_details': self._generate_mock_hourly_data(temperature, conditions[i % len(conditions)])
                })
            
            return forecast_list
            
        except Exception as e:
            logger.error(f"Error generating mock forecast: {str(e)}")
            return []
    
    def _generate_mock_day_forecast(self, date: datetime) -> Dict[str, Any]:
        """Generate mock forecast for a single day."""
        conditions = ['Sunny', 'Partly Cloudy', 'Cloudy', 'Clear']
        base_temp = 22
        day_of_year = date.timetuple().tm_yday
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'day_name': date.strftime('%A'),
            'temperature': base_temp + (day_of_year % 10) - 5,
            'condition': conditions[day_of_year % len(conditions)],
            'humidity': 60 + (day_of_year % 25),
            'precipitation': 0,
            'hourly_details': []
        }
    
    def _generate_mock_hourly_data(self, base_temp: float, condition: str) -> List[Dict[str, Any]]:
        """Generate mock hourly data for a day."""
        hourly_data = []
        
        for hour in range(8, 20, 3):  # Every 3 hours from 8 AM to 8 PM
            temp_variation = (hour - 14) * 0.5  # Peak at 2 PM
            hourly_data.append({
                'time': f"{hour:02d}:00",
                'temperature': round(base_temp + temp_variation, 1),
                'condition': condition,
                'humidity': 60 + (hour % 20),
                'wind_speed': 2.5 + (hour % 5),
                'precipitation': 0
            })
        
        return hourly_data
    
    def _get_mock_weather_data(self, destination: str, start_date: str, duration: int) -> Dict[str, Any]:
        """Get complete mock weather data when API is unavailable."""
        try:
            return {
                'success': True,
                'destination': destination,
                'current_weather': {
                    'temperature': 22,
                    'condition': 'Partly Cloudy',
                    'humidity': 65,
                    'wind_speed': 3.2,
                    'pressure': 1013
                },
                'forecast': self._generate_mock_forecast(start_date, duration),
                'source': 'Mock Data (API unavailable)',
                'note': 'Weather data is simulated. Please check actual weather conditions before travel.'
            }
            
        except Exception as e:
            logger.error(f"Error generating mock weather {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'forecast': []
            }
