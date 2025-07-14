import requests
import datetime
from typing import Dict, Any, List
from config.settings import OPENWEATHER_API_KEY, WEATHER_FORECAST_DAYS

class WeatherService:
    """负责获取实时和预测天气信息。"""

    def __init__(self):
        # 实际应用中，这里会配置天气API的基URL和API Key
        self.base_url = "http://api.openweathermap.org/data/2.5/"
        self.api_key = OPENWEATHER_API_KEY # 从settings.py获取

    def _get_weather_data(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        通用方法，用于向天气API发送请求并返回JSON数据。
        Args:
            endpoint: API的端点（例如："weather", "forecast"）。
            params: 请求参数字典。
        Returns:
            API返回的JSON数据。
        Raises:
            requests.exceptions.RequestException: 如果请求失败。
        """
        params["appid"] = self.api_key
        params["units"] = "metric" # 使用摄氏度
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status() # 检查HTTP错误
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data from {url}: {e}")
            raise

    def get_current_weather(self, city_name: str) -> Dict[str, Any]:
        """
        获取指定城市的实时天气信息。
        Args:
            city_name: 城市名称。
        Returns:
            包含实时天气信息的字典。
        """
        print(f"Getting current weather for {city_name}")
        try:
            data = self._get_weather_data("weather", {"q": city_name, "lang": "zh_cn"})
            return {
                "city": data.get("name"),
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "conditions": data["weather"][0]["description"],
                "icon": self._get_weather_icon(data["weather"][0]["icon"])
            }
        except Exception as e:
            print(f"Could not get current weather for {city_name}: {e}")
            return {}

    def get_daily_forecast(self, city_name: str, days: int = WEATHER_FORECAST_DAYS) -> List[Dict[str, Any]]:
        """
        获取指定城市未来几天的天气预报。
        Args:
            city_name: 城市名称。
            days: 预报天数。
        Returns:
            包含每日天气预报信息的列表。
        """
        print(f"Getting {days}-day forecast for {city_name}")
        forecast_data = []
        try:
            # OpenWeatherMap的forecast API提供的是每3小时的数据，需要处理成每日数据
            data = self._get_weather_data("forecast", {"q": city_name, "lang": "zh_cn"})
            
            daily_temps = {}
            daily_conditions = {}
            daily_humidity = {}
            daily_wind = {}
            daily_rain_prob = {}

            for item in data["list"]:
                dt_txt = item["dt_txt"]
                date = dt_txt.split(" ")[0] # YYYY-MM-DD
                
                if date not in daily_temps:
                    daily_temps[date] = {"min": float('inf'), "max": float('-inf')}
                    daily_conditions[date] = []
                    daily_humidity[date] = []
                    daily_wind[date] = []
                    daily_rain_prob[date] = []

                daily_temps[date]["min"] = min(daily_temps[date]["min"], item["main"]["temp_min"])
                daily_temps[date]["max"] = max(daily_temps[date]["max"], item["main"]["temp_max"])
                daily_conditions[date].append(item["weather"][0]["description"])
                daily_humidity[date].append(item["main"]["humidity"])
                daily_wind[date].append(item["wind"]["speed"])
                daily_rain_prob[date].append(item.get("pop", 0) * 100) # Probability of precipitation

            sorted_dates = sorted(daily_temps.keys())[:days]

            for d in sorted_dates:
                # 简单处理：取出现次数最多的天气状况
                conditions_counts = {cond: daily_conditions[d].count(cond) for cond in set(daily_conditions[d])}
                most_common_condition = max(conditions_counts, key=conditions_counts.get)
                
                # 简单处理：取平均湿度、风速、降雨概率
                avg_humidity = sum(daily_humidity[d]) / len(daily_humidity[d])
                avg_wind = sum(daily_wind[d]) / len(daily_wind[d])
                avg_rain_prob = sum(daily_rain_prob[d]) / len(daily_rain_prob[d])

                forecast_data.append({
                    "date": d,
                    "conditions": most_common_condition,
                    "icon": self._get_weather_icon_from_conditions(most_common_condition), # 根据条件获取图标
                    "min_temp": round(daily_temps[d]["min"]),
                    "max_temp": round(daily_temps[d]["max"]),
                    "humidity": round(avg_humidity),
                    "wind": f"{round(avg_wind)} m/s",
                    "rain_probability": round(avg_rain_prob),
                    "aqi": "良好", # 示例数据，实际需要AQI API
                    "uv_index": "中等", # 示例数据，实际需要UV API
                    "sunrise_sunset": "06:00/18:30", # 示例数据
                    "suggestions": ""
                })
        except Exception as e:
            print(f"Could not get daily forecast for {city_name}: {e}")
        return forecast_data

    def _get_weather_icon(self, icon_code: str) -> str:
        """
        根据OpenWeatherMap的图标代码返回一个表情符号图标。
        Args:
            icon_code: OpenWeatherMap的图标代码。
        Returns:
            对应的表情符号图标。
        """
        # 更多图标映射可以根据需要添加
        icon_map = {
            "01d": "☀️", "01n": "🌙",
            "02d": "🌤️", "02n": "☁️",
            "03d": "☁️", "03n": "☁️",
            "04d": "☁️", "04n": "☁️",
            "09d": "🌧️", "09n": "🌧️",
            "10d": "🌦️", "10n": "🌧️",
            "11d": "⛈️", "11n": "⛈️",
            "13d": "🌨️", "13n": "🌨️",
            "50d": "🌫️", "50n": "🌫️",
        }
        return icon_map.get(icon_code, "❓")

    def _get_weather_icon_from_conditions(self, conditions: str) -> str:
        """
        根据天气描述返回一个表情符号图标。
        Args:
            conditions: 天气描述字符串。
        Returns:
            对应的表情符号图标。
        """
        if "晴" in conditions: return "☀️"
        if "云" in conditions: return "☁️"
        if "雨" in conditions: return "🌧️"
        if "雪" in conditions: return "🌨️"
        if "雷" in conditions: return "⛈️"
        if "雾" in conditions or "霾" in conditions: return "🌫️"
        return "❓"

# 示例用法 (仅用于测试)
async def main():
    weather_service = WeatherService()
    # current_weather = weather_service.get_current_weather("北京")
    # print("Current Weather:", current_weather)
    # forecast = weather_service.get_daily_forecast("北京", days=7)
    # print("7-Day Forecast:", forecast)

if __name__ == "__main__":
    # 注意：直接运行此文件需要有效的API Key
    # 并且OpenWeatherMap的免费API对forecast的调用频率有限制
    # asyncio.run(main())
    pass
