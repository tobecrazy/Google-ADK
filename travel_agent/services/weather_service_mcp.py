"""
Enhanced Weather Service with Direct MCP Integration
Provides weather forecast data using Amap MCP server
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class MCPWeatherService:
    """Enhanced weather service with direct MCP integration."""
    
    def __init__(self):
        """Initialize the MCP weather service."""
        logger.info("MCP Weather Service initialized")
    
    def get_weather_forecast(
        self,
        destination: str,
        start_date: str,
        duration: int
    ) -> Dict[str, Any]:
        """
        Get weather forecast for travel dates using Amap MCP server.
        
        Args:
            destination: Destination city name
            start_date: Start date (YYYY-MM-DD)
            duration: Number of days
            
        Returns:
            Dict containing weather forecast data
        """
        try:
            logger.info(f"Getting weather forecast for {destination} from {start_date} for {duration} days")
            
            # This method will be called by the agent which has access to MCP tools
            # The actual MCP call will be made by the calling agent
            return {
                'success': True,
                'destination': destination,
                'start_date': start_date,
                'duration': duration,
                'forecast': [],
                'source': 'MCP Weather Service',
                'note': 'Weather data will be fetched using MCP tools by the agent.',
                'mcp_required': True,
                'mcp_server': 'amap-maps',
                'mcp_tool': 'maps_weather',
                'mcp_args': {'city': destination}
            }
            
        except Exception as e:
            logger.error(f"Error in MCP weather service for {destination}: {str(e)}")
            return self._create_error_response(
                f"MCP weather service error: {str(e)}",
                destination
            )
    
    def parse_amap_weather_response(self, response: Dict[str, Any], start_date: str, duration: int) -> Dict[str, Any]:
        """
        Parse Amap weather API response into standardized format.
        
        Args:
            response: Raw response from Amap weather API
            start_date: Start date for the forecast
            duration: Number of days requested
            
        Returns:
            Parsed weather data
        """
        try:
            if not response or 'forecasts' not in response:
                return self._create_error_response(
                    "Invalid weather response format",
                    response.get('city', 'Unknown')
                )
            
            forecasts = response['forecasts']
            city = response.get('city', 'Unknown')
            
            # Parse the forecast data
            parsed_forecasts = []
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            
            for i in range(duration):
                target_date = start_dt + timedelta(days=i)
                target_date_str = target_date.strftime('%Y-%m-%d')
                
                # Find matching forecast or use the closest available
                matching_forecast = None
                for forecast in forecasts:
                    if forecast.get('date') == target_date_str:
                        matching_forecast = forecast
                        break
                
                # If no exact match, use the first available forecast as template
                if not matching_forecast and forecasts:
                    matching_forecast = forecasts[0]
                
                if matching_forecast:
                    daily_forecast = {
                        'date': target_date_str,
                        'day_name': target_date.strftime('%A'),
                        'day_weather': matching_forecast.get('dayweather', '未知'),
                        'night_weather': matching_forecast.get('nightweather', '未知'),
                        'day_temp': matching_forecast.get('daytemp', 'N/A'),
                        'night_temp': matching_forecast.get('nighttemp', 'N/A'),
                        'day_temp_float': matching_forecast.get('daytemp_float'),
                        'night_temp_float': matching_forecast.get('nighttemp_float'),
                        'day_wind': matching_forecast.get('daywind', 'N/A'),
                        'night_wind': matching_forecast.get('nightwind', 'N/A'),
                        'day_wind_power': matching_forecast.get('daypower', 'N/A'),
                        'night_wind_power': matching_forecast.get('nightpower', 'N/A'),
                        'week_day': matching_forecast.get('week', 'N/A')
                    }
                    
                    # Add summary information
                    daily_forecast['summary'] = f"白天{daily_forecast['day_weather']}，{daily_forecast['day_temp']}°C；夜间{daily_forecast['night_weather']}，{daily_forecast['night_temp']}°C"
                    daily_forecast['temperature_range'] = f"{daily_forecast['night_temp']}°C - {daily_forecast['day_temp']}°C"
                    
                    parsed_forecasts.append(daily_forecast)
                else:
                    # Create placeholder if no data available
                    parsed_forecasts.append({
                        'date': target_date_str,
                        'day_name': target_date.strftime('%A'),
                        'summary': '天气数据暂不可用',
                        'temperature_range': 'N/A',
                        'day_weather': '未知',
                        'night_weather': '未知'
                    })
            
            logger.info(f"Successfully parsed {len(parsed_forecasts)} day forecast for {city}")
            
            return {
                'success': True,
                'destination': city,
                'forecast': parsed_forecasts,
                'source': 'Amap Weather API',
                'note': f'天气预报数据来自高德地图API，包含{len(parsed_forecasts)}天的详细预报信息。',
                'raw_data': response
            }
            
        except Exception as e:
            logger.error(f"Error parsing Amap weather response: {str(e)}")
            return self._create_error_response(
                f"Weather data parsing error: {str(e)}",
                response.get('city', 'Unknown') if response else 'Unknown'
            )
    
    def _create_error_response(self, error_message: str, destination: str) -> Dict[str, Any]:
        """
        Create standardized error response for weather service failures.
        
        Args:
            error_message: Description of the error
            destination: Destination that was queried
            
        Returns:
            Standardized error response dictionary
        """
        return {
            'success': False,
            'destination': destination,
            'error': error_message,
            'forecast': [],
            'source': 'MCP Weather Service Error',
            'note': '天气数据暂时无法获取，请在出行前通过天气应用或网站查看最新天气预报。',
            'suggestion': '建议使用天气应用或访问天气网站获取最新天气信息。'
        }

# Create a global instance
mcp_weather_service = MCPWeatherService()
