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
            logger.info(f"Getting weather forecast for {destination} from {start_date} for {duration} days")
            
            if not self.api_key:
                logger.warning("No weather API key available, using enhanced mock data")
                return self._get_enhanced_mock_weather_data(destination, start_date, duration)
            
            # Convert Chinese city names to Pinyin and try multiple variations
            city_queries = self._get_city_query_variations(destination)
            
            current_weather = None
            forecast_data = []
            
            # Try different city name variations
            for city_query in city_queries:
                logger.info(f"Trying weather query for: {city_query}")
                
                # Get current weather first to validate city
                current_weather = self._get_current_weather(city_query)
                if current_weather.get('success'):
                    # Get forecast data
                    forecast_data = self._get_forecast_data(city_query, start_date, duration)
                    if forecast_data:
                        break
                else:
                    logger.warning(f"Weather query failed for {city_query}")
            
            if not current_weather or not current_weather.get('success') or not forecast_data:
                logger.warning(f"Could not get accurate weather for {destination}, using enhanced mock data")
                return self._get_enhanced_mock_weather_data(destination, start_date, duration)
            
            return {
                'success': True,
                'destination': destination,
                'current_weather': current_weather.get('data', {}),
                'forecast': forecast_data,
                'source': 'OpenWeatherMap',
                'query_used': city_queries[0] if city_queries else destination
            }
            
        except Exception as e:
            logger.error(f"Error getting weather forecast: {str(e)}")
            return self._get_enhanced_mock_weather_data(destination, start_date, duration)
    
    def _get_city_query_variations(self, city: str) -> List[str]:
        """Get multiple variations of city name for weather queries."""
        try:
            variations = []
            
            # Add original city name
            variations.append(city)
            
            # Handle Chinese city names
            if any('\u4e00' <= char <= '\u9fff' for char in city):
                # Convert to Pinyin
                try:
                    pinyin_parts = pinyin(city, style=Style.NORMAL)
                    pinyin_name = "".join([part[0].capitalize() for part in pinyin_parts])
                    variations.append(pinyin_name)
                    
                    # Also try with spaces
                    pinyin_spaced = " ".join([part[0].capitalize() for part in pinyin_parts])
                    variations.append(pinyin_spaced)
                except:
                    pass
                
                # Common Chinese city mappings
                city_mappings = {
                    '西安': ['Xi\'an', 'Xian', 'Xi an'],
                    '北京': ['Beijing', 'Peking'],
                    '上海': ['Shanghai'],
                    '广州': ['Guangzhou', 'Canton'],
                    '深圳': ['Shenzhen'],
                    '成都': ['Chengdu'],
                    '重庆': ['Chongqing'],
                    '杭州': ['Hangzhou'],
                    '南京': ['Nanjing', 'Nanking'],
                    '武汉': ['Wuhan']
                }
                
                if city in city_mappings:
                    variations.extend(city_mappings[city])
            
            # Remove duplicates while preserving order
            seen = set()
            unique_variations = []
            for variation in variations:
                if variation not in seen:
                    seen.add(variation)
                    unique_variations.append(variation)
            
            logger.info(f"City query variations for {city}: {unique_variations}")
            return unique_variations
            
        except Exception as e:
            logger.warning(f"Error getting city variations: {str(e)}")
            return [city]
    
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
    
    def _get_enhanced_mock_weather_data(self, destination: str, start_date: str, duration: int) -> Dict[str, Any]:
        """Get enhanced mock weather data based on destination and season."""
        try:
            # Parse start date to determine season and location-appropriate weather
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            month = start_dt.month
            
            # Determine season-appropriate weather patterns
            weather_patterns = self._get_seasonal_weather_patterns(destination, month)
            
            return {
                'success': True,
                'destination': destination,
                'current_weather': {
                    'temperature': weather_patterns['base_temp'],
                    'condition': weather_patterns['common_conditions'][0],
                    'humidity': weather_patterns['humidity'],
                    'wind_speed': weather_patterns['wind_speed'],
                    'pressure': 1013
                },
                'forecast': self._generate_enhanced_mock_forecast(start_date, duration, weather_patterns),
                'source': 'Enhanced Mock Data (Seasonal patterns)',
                'note': 'Weather data is simulated based on seasonal patterns. Please check actual weather conditions before travel.'
            }
            
        except Exception as e:
            logger.error(f"Error generating enhanced mock weather: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'forecast': []
            }
    
    def _get_seasonal_weather_patterns(self, destination: str, month: int) -> Dict[str, Any]:
        """Get seasonal weather patterns for different destinations."""
        try:
            # Default patterns
            patterns = {
                'base_temp': 22,
                'temp_range': 8,
                'humidity': 65,
                'wind_speed': 3.2,
                'common_conditions': ['Partly Cloudy', 'Sunny', 'Cloudy'],
                'precipitation_chance': 0.2
            }
            
            # Adjust for Chinese cities and seasons
            if any('\u4e00' <= char <= '\u9fff' for char in destination):
                # Chinese city patterns
                if '西安' in destination:
                    if month in [12, 1, 2]:  # Winter
                        patterns.update({
                            'base_temp': 2,
                            'temp_range': 12,
                            'humidity': 55,
                            'common_conditions': ['Clear', 'Sunny', 'Partly Cloudy'],
                            'precipitation_chance': 0.1
                        })
                    elif month in [6, 7, 8]:  # Summer
                        patterns.update({
                            'base_temp': 28,
                            'temp_range': 10,
                            'humidity': 70,
                            'common_conditions': ['Hot', 'Sunny', 'Partly Cloudy'],
                            'precipitation_chance': 0.3
                        })
                    elif month in [3, 4, 5]:  # Spring
                        patterns.update({
                            'base_temp': 18,
                            'temp_range': 12,
                            'humidity': 60,
                            'common_conditions': ['Mild', 'Sunny', 'Breezy'],
                            'precipitation_chance': 0.2
                        })
                    else:  # Fall
                        patterns.update({
                            'base_temp': 15,
                            'temp_range': 10,
                            'humidity': 58,
                            'common_conditions': ['Cool', 'Clear', 'Crisp'],
                            'precipitation_chance': 0.15
                        })
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error getting seasonal patterns: {str(e)}")
            return {
                'base_temp': 22,
                'temp_range': 8,
                'humidity': 65,
                'wind_speed': 3.2,
                'common_conditions': ['Partly Cloudy', 'Sunny', 'Cloudy'],
                'precipitation_chance': 0.2
            }
    
    def _generate_enhanced_mock_forecast(self, start_date: str, duration: int, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate enhanced mock forecast based on seasonal patterns."""
        try:
            forecast_list = []
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            
            base_temp = patterns['base_temp']
            temp_range = patterns['temp_range']
            conditions = patterns['common_conditions']
            humidity = patterns['humidity']
            precip_chance = patterns['precipitation_chance']
            
            for i in range(duration):
                current_date = start_dt + timedelta(days=i)
                
                # Add some realistic variation
                temp_variation = (i % 7) - 3  # -3 to +3 degrees variation over week
                daily_temp = base_temp + temp_variation + ((i % 3) - 1)  # Additional daily variation
                
                # Determine condition based on patterns and some randomness
                condition_index = (i + hash(current_date.strftime('%Y-%m-%d'))) % len(conditions)
                condition = conditions[condition_index]
                
                # Add occasional precipitation
                if (i % 5 == 0) and (precip_chance > 0.15):
                    condition = 'Light Rain' if 'Rain' not in condition else condition
                
                forecast_list.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'day_name': current_date.strftime('%A'),
                    'temperature': max(daily_temp, -10),  # Reasonable minimum
                    'condition': condition,
                    'humidity': humidity + ((i % 4) * 5),  # Vary humidity slightly
                    'precipitation': 0.5 if 'Rain' in condition else 0,
                    'hourly_details': self._generate_mock_hourly_data(daily_temp, condition)
                })
            
            return forecast_list
            
        except Exception as e:
            logger.error(f"Error generating enhanced mock forecast: {str(e)}")
            return self._generate_mock_forecast(start_date, duration)
