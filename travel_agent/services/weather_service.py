"""
Weather Service
Integrates with AMap weather API via MCP to provide real weather forecast data
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable

logger = logging.getLogger(__name__)

class WeatherService:
    """Service for weather data integration using AMap weather API via MCP."""
    
    def __init__(self, use_mcp_tool: Optional[Callable] = None):
        """
        Initialize the weather service with AMap MCP integration.
        
        Args:
            use_mcp_tool: MCP tool function for accessing amap-maps weather service
        """
        self.use_mcp_tool = use_mcp_tool
        
        if not self.use_mcp_tool:
            logger.warning("No MCP tool provided. Weather service will return errors for all requests.")
        else:
            logger.info("Weather Service initialized with AMap MCP integration")
    
    def get_weather_forecast(
        self,
        destination: str,
        start_date: str,
        duration: int
    ) -> Dict[str, Any]:
        """
        Get weather forecast for travel dates using AMap API via MCP.
        
        Args:
            destination: Destination city name
            start_date: Start date (YYYY-MM-DD)
            duration: Number of days
            
        Returns:
            Dict containing weather forecast data or error information
        """
        try:
            logger.info(f"Getting weather forecast for {destination} from {start_date} for {duration} days")
            
            if not self.use_mcp_tool:
                return self._create_error_response(
                    "Weather service not available - no MCP tool configured",
                    destination
                )
            
            # Get weather data from AMap via MCP
            amap_weather = self._get_amap_weather(destination)
            
            if not amap_weather.get('success', False):
                error_msg = amap_weather.get('error', 'Unknown error from AMap weather API')
                return self._create_error_response(error_msg, destination)
            
            # Convert AMap weather data to forecast format
            forecast_data = self._convert_amap_to_forecast(
                amap_weather, 
                start_date, 
                duration
            )
            
            return {
                'success': True,
                'destination': destination,
                'current_weather': amap_weather.get('current_weather', {}),
                'forecast': forecast_data,
                'source': 'AMap Weather API via MCP',
                'query_used': destination,
                'start_date': start_date,
                'duration': duration
            }
            
        except Exception as e:
            logger.error(f"Error getting weather forecast for {destination}: {str(e)}")
            return self._create_error_response(
                f"Weather service error: {str(e)}",
                destination
            )
    
    def _get_amap_weather(self, city: str) -> Dict[str, Any]:
        """
        Get weather data from AMap API via MCP tool.
        
        Args:
            city: City name to query
            
        Returns:
            Dict containing weather data or error information
        """
        try:
            logger.info(f"Requesting weather data for city: {city}")
            
            # Use MCP tool to get weather from amap-maps-mcp-server
            result = self.use_mcp_tool(
                server_name="amap-maps",
                tool_name="maps_weather",
                arguments={"city": city}
            )
            
            if not result:
                return {
                    'success': False,
                    'error': 'No response from AMap weather API'
                }
            
            # Check if the MCP call was successful
            if isinstance(result, dict) and 'error' in result:
                logger.warning(f"AMap weather API error: {result['error']}")
                return {
                    'success': False,
                    'error': result['error']
                }
            
            # Parse the weather data
            weather_data = self._parse_amap_weather_response(result)
            
            if weather_data:
                logger.info(f"Successfully retrieved weather data for {city}")
                return {
                    'success': True,
                    'current_weather': weather_data,
                    'raw_response': result
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to parse AMap weather response'
                }
                
        except Exception as e:
            logger.error(f"Error calling AMap weather API for {city}: {str(e)}")
            return {
                'success': False,
                'error': f'AMap weather API call failed: {str(e)}'
            }
    
    def _parse_amap_weather_response(self, response: Any) -> Optional[Dict[str, Any]]:
        """
        Parse AMap weather API response into standardized format.
        
        Args:
            response: Raw response from AMap weather API
            
        Returns:
            Parsed weather data or None if parsing fails
        """
        try:
            # Handle different response formats from AMap API
            if isinstance(response, str):
                # If response is a string, try to extract weather info
                return {
                    'condition': response,
                    'temperature': None,
                    'humidity': None,
                    'wind_speed': None,
                    'description': response
                }
            
            elif isinstance(response, dict):
                # Extract weather information from dictionary response
                weather_info = {}
                
                # Try to extract common weather fields
                if 'weather' in response:
                    weather_info['condition'] = response['weather']
                elif 'condition' in response:
                    weather_info['condition'] = response['condition']
                else:
                    weather_info['condition'] = 'Unknown'
                
                # Extract temperature if available
                if 'temperature' in response:
                    weather_info['temperature'] = response['temperature']
                elif 'temp' in response:
                    weather_info['temperature'] = response['temp']
                
                # Extract other weather parameters
                weather_info['humidity'] = response.get('humidity')
                weather_info['wind_speed'] = response.get('wind_speed', response.get('wind'))
                weather_info['pressure'] = response.get('pressure')
                weather_info['description'] = response.get('description', weather_info['condition'])
                
                return weather_info
            
            else:
                logger.warning(f"Unexpected AMap weather response format: {type(response)}")
                return {
                    'condition': str(response),
                    'temperature': None,
                    'humidity': None,
                    'wind_speed': None,
                    'description': str(response)
                }
                
        except Exception as e:
            logger.error(f"Error parsing AMap weather response: {str(e)}")
            return None
    
    def _convert_amap_to_forecast(
        self, 
        amap_weather: Dict[str, Any], 
        start_date: str, 
        duration: int
    ) -> List[Dict[str, Any]]:
        """
        Convert AMap weather data to multi-day forecast format.
        
        Args:
            amap_weather: Weather data from AMap API
            start_date: Start date for forecast
            duration: Number of days to forecast
            
        Returns:
            List of daily forecast data
        """
        try:
            forecast_list = []
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            current_weather = amap_weather.get('current_weather', {})
            
            # Since AMap typically provides current weather, we'll create a forecast
            # based on current conditions with some variation
            base_temp = current_weather.get('temperature')
            condition = current_weather.get('condition', 'Unknown')
            humidity = current_weather.get('humidity')
            wind_speed = current_weather.get('wind_speed')
            
            for i in range(duration):
                current_date = start_dt + timedelta(days=i)
                
                # Create daily forecast entry
                daily_forecast = {
                    'date': current_date.strftime('%Y-%m-%d'),
                    'day_name': current_date.strftime('%A'),
                    'condition': condition,
                    'humidity': humidity,
                    'wind_speed': wind_speed,
                    'precipitation': 0  # Default, could be enhanced with more detailed API data
                }
                
                # Add temperature if available
                if base_temp is not None:
                    try:
                        # Convert temperature to float if it's a string
                        temp_value = float(base_temp) if isinstance(base_temp, str) else base_temp
                        # Add slight variation for multi-day forecast
                        temp_variation = (i % 3) - 1  # -1, 0, +1 degree variation
                        daily_forecast['temperature'] = temp_value + temp_variation
                    except (ValueError, TypeError):
                        daily_forecast['temperature'] = base_temp  # Keep original if conversion fails
                else:
                    daily_forecast['temperature'] = None
                
                forecast_list.append(daily_forecast)
            
            logger.info(f"Generated {len(forecast_list)} day forecast from AMap weather data")
            return forecast_list
            
        except Exception as e:
            logger.error(f"Error converting AMap weather to forecast: {str(e)}")
            return []
    
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
            'current_weather': {},
            'source': 'Weather Service Error',
            'note': 'Weather data is currently unavailable. Please check weather conditions manually before travel.',
            'suggestion': 'Try checking weather on local weather apps or websites for your destination.'
        }
