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
    """Service for weather data integration using AMap weather API."""
    
    def __init__(self, use_mcp_tool=None):
        """Initialize the weather service."""
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.use_mcp_tool = use_mcp_tool  # MCP tool function for amap weather
        
        if not self.api_key and not self.use_mcp_tool:
            logger.warning("No weather API available. Weather service will use mock data.")
        
        logger.info("Weather Service initialized with AMap MCP integration")
    
    def get_weather_forecast(
        self,
        destination: str,
        start_date: str,
        duration: int
    ) -> Dict[str, Any]:
        """
        Get weather forecast for travel dates using AMap API.
        
        Args:
            destination: Destination city
            start_date: Start date (YYYY-MM-DD)
            duration: Number of days
            
        Returns:
            Dict containing weather forecast data
        """
        try:
            logger.info(f"Getting weather forecast for {destination} from {start_date} for {duration} days")
            
            # First try to get weather from AMap MCP service
            if self.use_mcp_tool:
                try:
                    amap_weather = self._get_amap_weather(destination)
                    if amap_weather.get('success'):
                        # Convert AMap weather data to our format
                        forecast_data = self._convert_amap_to_forecast(amap_weather, start_date, duration)
                        return {
                            'success': True,
                            'destination': destination,
                            'current_weather': amap_weather.get('current_weather', {}),
                            'forecast': forecast_data,
                            'source': 'AMap Weather API',
                            'query_used': destination
                        }
                except Exception as amap_error:
                    logger.warning(f"AMap weather API failed: {str(amap_error)}")
            
            # Fallback to OpenWeatherMap if available
            if self.api_key:
                logger.info("Falling back to OpenWeatherMap API")
                return self._get_openweather_forecast(destination, start_date, duration)
            
            # Final fallback to enhanced mock data
            logger.warning(f"No weather API available, using enhanced mock data for {destination}")
            return self._get_enhanced_mock_weather_data(destination, start_date, duration)
            
        except Exception as e:
            logger.error(f"Error getting weather forecast: {str(e)}")
            return self._get_enhanced_mock_weather_data(destination, start_date, duration)
    
    def _get_city_query_variations(self, city: str) -> List[str]:
        """Get multiple variations of city name for weather queries."""
        try:
            variations = []
            
            # Handle Chinese city names first (prioritize mapped names)
            if any('\u4e00' <= char <= '\u9fff' for char in city):
                logger.info(f"Processing Chinese city name: {city}")
                
                # Enhanced Chinese city mappings with country codes
                city_mappings = {
                    '西安': ['Xi\'an', 'Xian', 'Xi an', 'Xi\'an,CN', 'Xian,CN'],
                    '北京': ['Beijing', 'Peking', 'Beijing,CN'],
                    '上海': ['Shanghai', 'Shanghai,CN'],
                    '广州': ['Guangzhou', 'Canton', 'Guangzhou,CN', 'Canton,CN'],
                    '深圳': ['Shenzhen', 'Shenzhen,CN'],
                    '成都': ['Chengdu', 'Chengdu,CN'],
                    '重庆': ['Chongqing', 'Chongqing,CN'],
                    '杭州': ['Hangzhou', 'Hangzhou,CN'],
                    '南京': ['Nanjing', 'Nanking', 'Nanjing,CN'],
                    '武汉': ['Wuhan', 'Wuhan,CN'],
                    '天津': ['Tianjin', 'Tientsin', 'Tianjin,CN'],
                    '苏州': ['Suzhou', 'Suzhou,CN'],
                    '青岛': ['Qingdao', 'Tsingtao', 'Qingdao,CN'],
                    '大连': ['Dalian', 'Dairen', 'Dalian,CN'],
                    '厦门': ['Xiamen', 'Amoy', 'Xiamen,CN'],
                    '昆明': ['Kunming', 'Kunming,CN'],
                    '长沙': ['Changsha', 'Changsha,CN'],
                    '郑州': ['Zhengzhou', 'Zhengzhou,CN'],
                    '济南': ['Jinan', 'Tsinan', 'Jinan,CN'],
                    '哈尔滨': ['Harbin', 'Harbin,CN'],
                    '沈阳': ['Shenyang', 'Mukden', 'Shenyang,CN'],
                    '长春': ['Changchun', 'Changchun,CN'],
                    '石家庄': ['Shijiazhuang', 'Shijiazhuang,CN'],
                    '太原': ['Taiyuan', 'Taiyuan,CN'],
                    '呼和浩特': ['Hohhot', 'Huhhot', 'Hohhot,CN'],
                    '乌鲁木齐': ['Urumqi', 'Urumchi', 'Urumqi,CN'],
                    '拉萨': ['Lhasa', 'Lasa', 'Lhasa,CN'],
                    '银川': ['Yinchuan', 'Yinchuan,CN'],
                    '西宁': ['Xining', 'Sining', 'Xining,CN'],
                    '兰州': ['Lanzhou', 'Lanchow', 'Lanzhou,CN'],
                    '海口': ['Haikou', 'Haikou,CN'],
                    '三亚': ['Sanya', 'Sanya,CN'],
                    '桂林': ['Guilin', 'Kweilin', 'Guilin,CN'],
                    '南宁': ['Nanning', 'Nanning,CN'],
                    '贵阳': ['Guiyang', 'Kweiyang', 'Guiyang,CN'],
                    '福州': ['Fuzhou', 'Foochow', 'Fuzhou,CN'],
                    '合肥': ['Hefei', 'Hofei', 'Hefei,CN'],
                    '南昌': ['Nanchang', 'Nanchang,CN']
                }
                
                # First, try exact mappings
                if city in city_mappings:
                    variations.extend(city_mappings[city])
                    logger.info(f"Found exact mapping for {city}: {city_mappings[city]}")
                
                # Try Pinyin conversion as backup
                try:
                    pinyin_parts = pinyin(city, style=Style.NORMAL)
                    if pinyin_parts:
                        # Capitalize each part and join
                        pinyin_name = "".join([part[0].capitalize() for part in pinyin_parts])
                        if pinyin_name not in variations:
                            variations.append(pinyin_name)
                            variations.append(f"{pinyin_name},CN")
                        
                        # Also try with spaces
                        pinyin_spaced = " ".join([part[0].capitalize() for part in pinyin_parts])
                        if pinyin_spaced not in variations:
                            variations.append(pinyin_spaced)
                            variations.append(f"{pinyin_spaced},CN")
                        
                        logger.info(f"Generated Pinyin variations: {pinyin_name}, {pinyin_spaced}")
                except Exception as pinyin_error:
                    logger.warning(f"Pinyin conversion failed for {city}: {str(pinyin_error)}")
                
                # Add original city name as last resort
                variations.append(city)
            else:
                # For non-Chinese cities, add original name first
                variations.append(city)
                
                # Add country code variations for common international cities
                if ',' not in city:  # Don't add country code if already present
                    # Try adding common country codes
                    common_countries = ['US', 'UK', 'CA', 'AU', 'DE', 'FR', 'IT', 'ES', 'JP', 'KR']
                    for country in common_countries:
                        variations.append(f"{city},{country}")
            
            # Remove duplicates while preserving order
            seen = set()
            unique_variations = []
            for variation in variations:
                if variation and variation not in seen:
                    seen.add(variation)
                    unique_variations.append(variation)
            
            logger.info(f"Final city query variations for '{city}': {unique_variations}")
            return unique_variations
            
        except Exception as e:
            logger.error(f"Error getting city variations for '{city}': {str(e)}")
            return [city]
    
    def _get_current_weather(self, city: str) -> Dict[str, Any]:
        """Get current weather for city validation."""
        try:
            # Check if API key is valid
            if not self.api_key :
                logger.warning(f"Invalid or demo API key detected for weather service")
                return {
                    'success': False,
                    'error': 'Invalid API key - using fallback data'
                }
            
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'en'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            # Handle different HTTP status codes
            if response.status_code == 404:
                logger.warning(f"City '{city}' not found in weather API")
                return {
                    'success': False,
                    'error': f'City not found: {city}'
                }
            elif response.status_code == 401:
                logger.error(f"Weather API authentication failed - invalid API key")
                return {
                    'success': False,
                    'error': 'Weather API authentication failed'
                }
            elif response.status_code == 429:
                logger.warning(f"Weather API rate limit exceeded")
                return {
                    'success': False,
                    'error': 'Weather API rate limit exceeded'
                }
            
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
                logger.warning(f"Weather API returned error code: {data.get('cod')} - {data.get('message')}")
                return {
                    'success': False,
                    'error': data.get('message', 'Unknown weather API error')
                }
                
        except requests.exceptions.Timeout:
            logger.error(f"Weather API request timeout for city: {city}")
            return {
                'success': False,
                'error': 'Weather API request timeout'
            }
        except requests.exceptions.ConnectionError:
            logger.error(f"Weather API connection error for city: {city}")
            return {
                'success': False,
                'error': 'Weather API connection error'
            }
        except Exception as e:
            logger.error(f"Unexpected error getting current weather for {city}: {str(e)}")
            return {
                'success': False,
                'error': f'Weather service error: {str(e)}'
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
            
            # Mock weather conditions in Chinese
            conditions = ['晴天', '局部多云', '多云', '小雨', '晴朗']
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
        conditions = ['晴天', '局部多云', '多云', '晴朗']
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
                logger.info(f"Applying seasonal patterns for Chinese city: {destination}, month: {month}")
                
                # Guangzhou (广州) - Subtropical climate
                if '广州' in destination:
                    if month in [12, 1, 2]:  # Winter
                        patterns.update({
                            'base_temp': 15,
                            'temp_range': 8,
                            'humidity': 70,
                            'common_conditions': ['Mild', 'Partly Cloudy', 'Overcast'],
                            'precipitation_chance': 0.15
                        })
                    elif month in [6, 7, 8]:  # Summer
                        patterns.update({
                            'base_temp': 30,
                            'temp_range': 6,
                            'humidity': 85,
                            'common_conditions': ['Hot and Humid', 'Thunderstorms', 'Partly Cloudy'],
                            'precipitation_chance': 0.6
                        })
                    elif month in [3, 4, 5]:  # Spring
                        patterns.update({
                            'base_temp': 24,
                            'temp_range': 8,
                            'humidity': 80,
                            'common_conditions': ['Warm', 'Rainy', 'Humid'],
                            'precipitation_chance': 0.4
                        })
                    else:  # Fall (9, 10, 11)
                        patterns.update({
                            'base_temp': 26,
                            'temp_range': 6,
                            'humidity': 75,
                            'common_conditions': ['Pleasant', 'Sunny', 'Comfortable'],
                            'precipitation_chance': 0.2
                        })
                
                # Xi'an (西安) - Continental climate
                elif '西安' in destination:
                    if month in [12, 1, 2]:  # Winter
                        patterns.update({
                            'base_temp': 2,
                            'temp_range': 12,
                            'humidity': 55,
                            'common_conditions': ['Cold', 'Clear', 'Dry'],
                            'precipitation_chance': 0.1
                        })
                    elif month in [6, 7, 8]:  # Summer
                        patterns.update({
                            'base_temp': 28,
                            'temp_range': 10,
                            'humidity': 70,
                            'common_conditions': ['Hot', 'Sunny', 'Occasional Rain'],
                            'precipitation_chance': 0.3
                        })
                    elif month in [3, 4, 5]:  # Spring
                        patterns.update({
                            'base_temp': 18,
                            'temp_range': 12,
                            'humidity': 60,
                            'common_conditions': ['Mild', 'Windy', 'Variable'],
                            'precipitation_chance': 0.2
                        })
                    else:  # Fall
                        patterns.update({
                            'base_temp': 15,
                            'temp_range': 10,
                            'humidity': 58,
                            'common_conditions': ['Cool', 'Clear', 'Comfortable'],
                            'precipitation_chance': 0.15
                        })
                
                # Beijing (北京) - Continental climate
                elif '北京' in destination:
                    if month in [12, 1, 2]:  # Winter
                        patterns.update({
                            'base_temp': -2,
                            'temp_range': 15,
                            'humidity': 45,
                            'common_conditions': ['Cold', 'Dry', 'Clear'],
                            'precipitation_chance': 0.05
                        })
                    elif month in [6, 7, 8]:  # Summer
                        patterns.update({
                            'base_temp': 27,
                            'temp_range': 8,
                            'humidity': 75,
                            'common_conditions': ['Hot', 'Humid', 'Thunderstorms'],
                            'precipitation_chance': 0.4
                        })
                    elif month in [3, 4, 5]:  # Spring
                        patterns.update({
                            'base_temp': 16,
                            'temp_range': 12,
                            'humidity': 55,
                            'common_conditions': ['Mild', 'Windy', 'Dusty'],
                            'precipitation_chance': 0.15
                        })
                    else:  # Fall
                        patterns.update({
                            'base_temp': 14,
                            'temp_range': 10,
                            'humidity': 60,
                            'common_conditions': ['Pleasant', 'Clear', 'Crisp'],
                            'precipitation_chance': 0.1
                        })
                
                # Shanghai (上海) - Subtropical climate
                elif '上海' in destination:
                    if month in [12, 1, 2]:  # Winter
                        patterns.update({
                            'base_temp': 6,
                            'temp_range': 8,
                            'humidity': 70,
                            'common_conditions': ['Cool', 'Damp', 'Overcast'],
                            'precipitation_chance': 0.2
                        })
                    elif month in [6, 7, 8]:  # Summer
                        patterns.update({
                            'base_temp': 29,
                            'temp_range': 6,
                            'humidity': 85,
                            'common_conditions': ['Hot', 'Humid', 'Rainy'],
                            'precipitation_chance': 0.5
                        })
                    elif month in [3, 4, 5]:  # Spring
                        patterns.update({
                            'base_temp': 19,
                            'temp_range': 10,
                            'humidity': 75,
                            'common_conditions': ['Mild', 'Rainy', 'Variable'],
                            'precipitation_chance': 0.35
                        })
                    else:  # Fall
                        patterns.update({
                            'base_temp': 21,
                            'temp_range': 8,
                            'humidity': 70,
                            'common_conditions': ['Pleasant', 'Comfortable', 'Sunny'],
                            'precipitation_chance': 0.2
                        })
                
                # Shenzhen (深圳) - Similar to Guangzhou
                elif '深圳' in destination:
                    if month in [12, 1, 2]:  # Winter
                        patterns.update({
                            'base_temp': 17,
                            'temp_range': 6,
                            'humidity': 65,
                            'common_conditions': ['Mild', 'Pleasant', 'Dry'],
                            'precipitation_chance': 0.1
                        })
                    elif month in [6, 7, 8]:  # Summer
                        patterns.update({
                            'base_temp': 31,
                            'temp_range': 5,
                            'humidity': 85,
                            'common_conditions': ['Hot', 'Humid', 'Thunderstorms'],
                            'precipitation_chance': 0.65
                        })
                    elif month in [3, 4, 5]:  # Spring
                        patterns.update({
                            'base_temp': 25,
                            'temp_range': 7,
                            'humidity': 80,
                            'common_conditions': ['Warm', 'Humid', 'Rainy'],
                            'precipitation_chance': 0.4
                        })
                    else:  # Fall
                        patterns.update({
                            'base_temp': 27,
                            'temp_range': 5,
                            'humidity': 70,
                            'common_conditions': ['Warm', 'Comfortable', 'Pleasant'],
                            'precipitation_chance': 0.15
                        })
                
                # Chengdu (成都) - Basin climate
                elif '成都' in destination:
                    if month in [12, 1, 2]:  # Winter
                        patterns.update({
                            'base_temp': 8,
                            'temp_range': 8,
                            'humidity': 80,
                            'common_conditions': ['Cool', 'Foggy', 'Overcast'],
                            'precipitation_chance': 0.15
                        })
                    elif month in [6, 7, 8]:  # Summer
                        patterns.update({
                            'base_temp': 26,
                            'temp_range': 6,
                            'humidity': 85,
                            'common_conditions': ['Warm', 'Humid', 'Rainy'],
                            'precipitation_chance': 0.6
                        })
                    elif month in [3, 4, 5]:  # Spring
                        patterns.update({
                            'base_temp': 19,
                            'temp_range': 8,
                            'humidity': 75,
                            'common_conditions': ['Mild', 'Rainy', 'Humid'],
                            'precipitation_chance': 0.4
                        })
                    else:  # Fall
                        patterns.update({
                            'base_temp': 18,
                            'temp_range': 8,
                            'humidity': 80,
                            'common_conditions': ['Pleasant', 'Overcast', 'Mild'],
                            'precipitation_chance': 0.3
                        })
                
                # Default for other Chinese cities
                else:
                    logger.info(f"Using default Chinese city patterns for {destination}")
                    if month in [12, 1, 2]:  # Winter
                        patterns.update({
                            'base_temp': 5,
                            'temp_range': 12,
                            'humidity': 60,
                            'common_conditions': ['Cold', 'Clear', 'Dry'],
                            'precipitation_chance': 0.1
                        })
                    elif month in [6, 7, 8]:  # Summer
                        patterns.update({
                            'base_temp': 28,
                            'temp_range': 8,
                            'humidity': 75,
                            'common_conditions': ['Hot', 'Humid', 'Rainy'],
                            'precipitation_chance': 0.4
                        })
                    elif month in [3, 4, 5]:  # Spring
                        patterns.update({
                            'base_temp': 18,
                            'temp_range': 10,
                            'humidity': 65,
                            'common_conditions': ['Mild', 'Variable', 'Pleasant'],
                            'precipitation_chance': 0.25
                        })
                    else:  # Fall
                        patterns.update({
                            'base_temp': 16,
                            'temp_range': 10,
                            'humidity': 65,
                            'common_conditions': ['Cool', 'Pleasant', 'Clear'],
                            'precipitation_chance': 0.2
                        })
            
            logger.info(f"Applied weather patterns for {destination}: {patterns}")
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
