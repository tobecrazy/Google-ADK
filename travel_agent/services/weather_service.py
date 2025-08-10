"""
Weather Service
Provides weather forecast data for travel planning
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable

logger = logging.getLogger(__name__)

class WeatherService:
    """Service for weather data integration."""
    
    def __init__(self, use_mcp_tool=None):
        """Initialize the weather service with optional MCP tool function."""
        self.use_mcp_tool = use_mcp_tool
        logger.info(f"Weather Service initialized with MCP integration: {'enabled' if use_mcp_tool else 'disabled'}")
    
    def get_weather_forecast(
        self,
        destination: str,
        start_date: str,
        duration: int
    ) -> Dict[str, Any]:
        """
        Get weather forecast for travel dates using real weather data from AMap API.
        
        Args:
            destination: Destination city name
            start_date: Start date (YYYY-MM-DD)
            duration: Number of days
            
        Returns:
            Dict containing weather forecast data
        """
        try:
            logger.info(f"Getting real weather forecast for {destination} from {start_date} for {duration} days")
            
            # Try to get real weather data from AMap API via MCP tool
            if self.use_mcp_tool:
                logger.info(f"Using MCP tool to get real weather data for {destination}")
                amap_weather = self._get_amap_weather(destination)
                
                if amap_weather['success']:
                    # Convert real weather data to multi-day forecast
                    forecast = self._convert_amap_to_forecast(amap_weather, start_date, duration)
                    
                    if forecast:
                        logger.info(f"Successfully generated {len(forecast)} day forecast from real weather data")
                        return {
                            'success': True,
                            'destination': destination,
                            'forecast': forecast,
                            'current_weather': amap_weather.get('current_weather', {}),
                            'source': 'AMap Real Weather Data',
                            'note': 'Weather forecast based on current real weather conditions from AMap API.',
                            'raw_data': amap_weather.get('raw_response')
                        }
                    else:
                        logger.warning(f"Failed to convert AMap weather data to forecast for {destination}")
                else:
                    logger.warning(f"Failed to get real weather data for {destination}: {amap_weather.get('error', 'Unknown error')}")
            else:
                logger.warning("MCP tool not available for weather service")
            
            # Fallback: Return error response indicating real weather is unavailable
            return self._create_error_response(
                "Real weather data is currently unavailable. MCP weather service may be offline or API key missing.",
                destination
            )
            
        except Exception as e:
            logger.error(f"Error getting weather forecast for {destination}: {str(e)}")
            return self._create_error_response(
                f"Weather service error: {str(e)}",
                destination
            )
    
    
    def _translate_condition_to_chinese(self, condition: str) -> str:
        """Translate weather conditions from English to Chinese."""
        translation_map = {
            'Sunny': '晴天',
            'Clear': '晴朗',
            'Partly Cloudy': '局部多云',
            'Cloudy': '多云',
            'Overcast': '阴天',
            'Rainy': '雨天',
            'Light Rain': '小雨',
            'Heavy Rain': '大雨',
            'Thunderstorm': '雷雨',
            'Foggy': '雾天',
            'Windy': '大风',
            'Snow': '雪天',
            'Drizzle': '毛毛雨'
        }
        
        return translation_map.get(condition, condition)
    
    def _get_amap_weather(self, city: str) -> Dict[str, Any]:
        """
        Get weather data from AMap API via MCP tool.
        
        Args:
            city: City name to query
            
        Returns:
            Dict containing weather data or error information
        """
        try:
            logger.info(f"🌍 Requesting weather data for city: {city}")
            
            if not self.use_mcp_tool:
                logger.error("❌ MCP tool function not available")
                return {
                    'success': False,
                    'error': 'MCP tool function not available'
                }
            
            # Use MCP tool to get weather from amap-maps-mcp-server
            logger.info(f"🔧 Calling MCP tool: maps_weather for {city}")
            result = self.use_mcp_tool(
                tool_name="maps_weather",
                arguments={"city": city},
                server_name="amap-maps"
            )
            
            logger.info(f"📡 MCP tool response type: {type(result)}")
            logger.info(f"📋 MCP tool response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            logger.debug(f"📋 MCP tool raw response: {result}")
            
            if not result:
                logger.error("❌ No response from AMap weather API")
                return {
                    'success': False,
                    'error': 'No response from AMap weather API'
                }
            
            # Handle different MCP response formats
            if isinstance(result, dict):
                # Check if it's an MCP error response
                if 'success' in result and not result['success']:
                    error_msg = result.get('error', 'Unknown error')
                    logger.warning(f"⚠️ MCP tool returned error: {error_msg}")
                    
                    # Check for specific error types
                    if 'event loop' in error_msg.lower():
                        logger.error("🔄 Event loop conflict detected in MCP call")
                        return {
                            'success': False,
                            'error': f"MCP tool error: {error_msg}",
                            'error_type': 'event_loop_conflict',
                            'suggestion': 'Event loop conflict - this should be fixed by the new async handling'
                        }
                    
                    return {
                        'success': False,
                        'error': f"MCP tool error: {error_msg}",
                        'error_type': 'mcp_tool_error'
                    }
                
                # Check for direct error field
                if 'error' in result and not result.get('success', True):
                    logger.warning(f"⚠️ AMap weather API error: {result['error']}")
                    return {
                        'success': False,
                        'error': result['error'],
                        'error_type': 'amap_api_error'
                    }
            
            # Parse the weather data
            logger.info("🔍 Attempting to parse weather response")
            weather_data = self._parse_amap_weather_response(result)
            
            if weather_data:
                logger.info(f"✅ Successfully retrieved weather data for {city}")
                logger.info(f"🌤️ Weather condition: {weather_data.get('condition', 'Unknown')}")
                logger.info(f"🌡️ Temperature: {weather_data.get('temperature', 'N/A')}°C")
                return {
                    'success': True,
                    'current_weather': weather_data,
                    'raw_response': result
                }
            else:
                logger.error("❌ Failed to parse AMap weather response")
                logger.error(f"📋 Unparseable response: {result}")
                return {
                    'success': False,
                    'error': 'Failed to parse AMap weather response - invalid format',
                    'raw_response': result,
                    'error_type': 'parsing_error'
                }
                
        except Exception as e:
            logger.error(f"💥 Exception calling AMap weather API for {city}: {str(e)}")
            logger.error(f"🔍 Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"📋 Full traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f'AMap weather API call failed: {str(e)}',
                'error_type': 'exception',
                'exception_type': type(e).__name__
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
            logger.info(f"🔍 Parsing AMap weather response: {type(response)}")
            logger.debug(f"📋 Raw response content: {response}")
            
            # Handle different response formats from AMap API
            if isinstance(response, str):
                logger.info("📝 Processing string response")
                return {
                    'condition': response,
                    'temperature': None,
                    'humidity': None,
                    'wind_speed': None,
                    'description': response,
                    'city': 'Unknown'
                }
            
            elif isinstance(response, dict):
                logger.info(f"📊 Processing dict response with keys: {list(response.keys())}")
                
                # Check if this is the standard Amap weather response format
                if 'forecasts' in response and isinstance(response['forecasts'], list):
                    forecasts = response['forecasts']
                    logger.info(f"🌤️ Found {len(forecasts)} forecast entries")
                    
                    if len(forecasts) > 0:
                        current_forecast = forecasts[0]
                        logger.info(f"📅 Using first forecast: {current_forecast.get('date', 'Unknown date')}")
                        
                        # Extract weather information from the first forecast
                        weather_info = {
                            'condition': current_forecast.get('dayweather', 'Unknown'),
                            'night_condition': current_forecast.get('nightweather', 'Unknown'),
                            'temperature': current_forecast.get('daytemp'),
                            'night_temperature': current_forecast.get('nighttemp'),
                            'temperature_float': current_forecast.get('daytemp_float'),
                            'night_temperature_float': current_forecast.get('nighttemp_float'),
                            'wind_direction': current_forecast.get('daywind'),
                            'night_wind_direction': current_forecast.get('nightwind'),
                            'wind_power': current_forecast.get('daypower'),
                            'night_wind_power': current_forecast.get('nightpower'),
                            'date': current_forecast.get('date'),
                            'week': current_forecast.get('week'),
                            'city': response.get('city', 'Unknown'),
                            'description': f"白天{current_forecast.get('dayweather', 'Unknown')}，{current_forecast.get('daytemp', 'N/A')}°C；夜间{current_forecast.get('nightweather', 'Unknown')}，{current_forecast.get('nighttemp', 'N/A')}°C"
                        }
                        
                        logger.info(f"✅ Successfully parsed Amap weather data for {weather_info['city']}")
                        logger.debug(f"🌡️ Weather details: {weather_info['description']}")
                        return weather_info
                    else:
                        logger.warning("⚠️ Amap weather response has empty forecasts array")
                        return None
                        
                # Handle MCP tool response format (nested result)
                elif 'result' in response and isinstance(response['result'], dict):
                    logger.info("🔄 Processing MCP tool response format")
                    return self._parse_amap_weather_response(response['result'])
                
                # Handle success/error response format
                elif 'success' in response:
                    if response.get('success') and 'result' in response:
                        logger.info("✅ Processing successful MCP response")
                        return self._parse_amap_weather_response(response['result'])
                    else:
                        logger.error(f"❌ MCP response indicates failure: {response.get('error', 'Unknown error')}")
                        return None
                
                else:
                    # Try to extract common weather fields for other formats
                    logger.info("🔍 Attempting to parse alternative response format")
                    weather_info = {}
                    
                    # Try different field names for weather condition
                    for field in ['weather', 'condition', 'dayweather']:
                        if field in response:
                            weather_info['condition'] = response[field]
                            break
                    else:
                        weather_info['condition'] = 'Unknown'
                    
                    # Try different field names for temperature
                    for field in ['temperature', 'temp', 'daytemp']:
                        if field in response:
                            weather_info['temperature'] = response[field]
                            break
                    
                    # Extract other weather parameters
                    weather_info['humidity'] = response.get('humidity')
                    weather_info['wind_speed'] = response.get('wind_speed', response.get('wind'))
                    weather_info['pressure'] = response.get('pressure')
                    weather_info['city'] = response.get('city', 'Unknown')
                    weather_info['description'] = response.get('description', weather_info['condition'])
                    
                    logger.info(f"🔧 Parsed alternative format for {weather_info.get('city', 'Unknown')}")
                    return weather_info
            
            else:
                logger.warning(f"⚠️ Unexpected AMap weather response format: {type(response)}")
                return {
                    'condition': str(response),
                    'temperature': None,
                    'humidity': None,
                    'wind_speed': None,
                    'description': str(response),
                    'city': 'Unknown'
                }
                
        except Exception as e:
            logger.error(f"❌ Error parsing AMap weather response: {str(e)}")
            logger.error(f"📋 Response that caused error: {response}")
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
            
            # Get the raw response which contains the forecasts array
            raw_response = amap_weather.get('raw_response', {})
            
            # Check if we have the forecasts data from Amap
            if isinstance(raw_response, dict) and 'forecasts' in raw_response:
                amap_forecasts = raw_response['forecasts']
                logger.info(f"Found {len(amap_forecasts)} forecast entries from Amap")
                
                # Use actual Amap forecast data for the requested duration
                for i in range(duration):
                    current_date = start_dt + timedelta(days=i)
                    date_str = current_date.strftime('%Y-%m-%d')
                    
                    # Find matching forecast from Amap data
                    matching_forecast = None
                    for forecast in amap_forecasts:
                        if forecast.get('date') == date_str:
                            matching_forecast = forecast
                            break
                    
                    # If no exact match, use the closest available or the first one
                    if not matching_forecast and len(amap_forecasts) > 0:
                        # Use the forecast closest to the requested date
                        if i < len(amap_forecasts):
                            matching_forecast = amap_forecasts[i]
                        else:
                            matching_forecast = amap_forecasts[-1]  # Use last available
                    
                    if matching_forecast:
                        # Create detailed forecast entry from Amap data
                        daily_forecast = {
                            'date': date_str,
                            'day_name': current_date.strftime('%A'),
                            'day_weather': matching_forecast.get('dayweather', 'Unknown'),
                            'night_weather': matching_forecast.get('nightweather', 'Unknown'),
                            'day_temp': matching_forecast.get('daytemp', 'N/A'),
                            'night_temp': matching_forecast.get('nighttemp', 'N/A'),
                            'day_temp_float': matching_forecast.get('daytemp_float'),
                            'night_temp_float': matching_forecast.get('nighttemp_float'),
                            'day_wind': matching_forecast.get('daywind', 'N/A'),
                            'night_wind': matching_forecast.get('nightwind', 'N/A'),
                            'day_wind_power': matching_forecast.get('daypower', 'N/A'),
                            'night_wind_power': matching_forecast.get('nightpower', 'N/A'),
                            'week_day': matching_forecast.get('week', 'N/A'),
                            'condition': matching_forecast.get('dayweather', 'Unknown'),
                            'temperature': matching_forecast.get('daytemp'),
                            'summary': f"白天{matching_forecast.get('dayweather', 'Unknown')}，{matching_forecast.get('daytemp', 'N/A')}°C；夜间{matching_forecast.get('nightweather', 'Unknown')}，{matching_forecast.get('nighttemp', 'N/A')}°C",
                            'temperature_range': f"{matching_forecast.get('nighttemp', 'N/A')}°C - {matching_forecast.get('daytemp', 'N/A')}°C"
                        }
                    else:
                        # Create placeholder if no forecast data available
                        daily_forecast = {
                            'date': date_str,
                            'day_name': current_date.strftime('%A'),
                            'condition': 'Unknown',
                            'temperature': None,
                            'summary': '天气数据暂不可用',
                            'temperature_range': 'N/A'
                        }
                    
                    forecast_list.append(daily_forecast)
            else:
                # Fallback: use current weather data if available
                current_weather = amap_weather.get('current_weather', {})
                base_temp = current_weather.get('temperature')
                condition = current_weather.get('condition', 'Unknown')
                
                logger.info("Using current weather data as fallback for forecast")
                
                for i in range(duration):
                    current_date = start_dt + timedelta(days=i)
                    
                    # Create daily forecast entry with variation
                    daily_forecast = {
                        'date': current_date.strftime('%Y-%m-%d'),
                        'day_name': current_date.strftime('%A'),
                        'condition': condition,
                        'summary': f"预计{condition}",
                        'temperature_range': 'N/A'
                    }
                    
                    # Add temperature if available
                    if base_temp is not None:
                        try:
                            temp_value = float(base_temp) if isinstance(base_temp, str) else base_temp
                            temp_variation = (i % 3) - 1  # -1, 0, +1 degree variation
                            daily_forecast['temperature'] = temp_value + temp_variation
                            daily_forecast['temperature_range'] = f"{temp_value + temp_variation - 2}°C - {temp_value + temp_variation + 2}°C"
                        except (ValueError, TypeError):
                            daily_forecast['temperature'] = base_temp
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
        logger.warning(f"⚠️ Creating error response for {destination}: {error_message}")
        
        # Create a basic forecast with placeholder data
        placeholder_forecast = []
        try:
            from datetime import datetime, timedelta
            today = datetime.now()
            for i in range(3):  # 3-day placeholder forecast
                forecast_date = today + timedelta(days=i)
                placeholder_forecast.append({
                    'date': forecast_date.strftime('%Y-%m-%d'),
                    'day_name': forecast_date.strftime('%A'),
                    'condition': '天气数据不可用',
                    'temperature': None,
                    'summary': f'第{i+1}天天气信息暂时无法获取',
                    'temperature_range': 'N/A',
                    'note': '请查看其他天气应用获取准确信息'
                })
        except Exception as e:
            logger.error(f"Error creating placeholder forecast: {str(e)}")
        
        return {
            'success': False,
            'destination': destination,
            'error': error_message,
            'forecast': placeholder_forecast,
            'current_weather': {
                'condition': '数据不可用',
                'temperature': None,
                'description': f'{destination}的天气信息暂时无法获取',
                'city': destination
            },
            'source': 'Weather Service Error',
            'note': '天气数据暂时无法获取，建议在出行前通过其他渠道查看天气预报。',
            'suggestion': '推荐使用手机天气应用、天气网站或询问当地人获取最新天气信息。',
            'troubleshooting': {
                'possible_causes': [
                    'MCP天气服务暂时不可用',
                    'API密钥配置问题',
                    '网络连接问题',
                    '城市名称识别问题'
                ],
                'recommendations': [
                    '检查网络连接',
                    '尝试使用不同的城市名称格式',
                    '稍后重试',
                    '使用备用天气信息源'
                ]
            }
        }
