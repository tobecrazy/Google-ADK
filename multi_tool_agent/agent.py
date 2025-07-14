import datetime
import os
import requests
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from pypinyin import pinyin, Style

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if not OPENWEATHER_API_KEY:
        return {
            "status": "error",
            "error_message": "OpenWeather API key is not set.",
        }

    # Convert Chinese city names to Pinyin with capitalization
    city_query = city
    if any('\u4e00' <= char <= '\u9fff' for char in city):
        pinyin_parts = pinyin(city, style=Style.NORMAL)
        # Join parts and capitalize the first letter of each part
        city_query = "".join([part[0].capitalize() for part in pinyin_parts])

    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city_query}&appid={OPENWEATHER_API_KEY}&units=metric&lang=zh_cn"
    
    try:
        response = requests.get(complete_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        if data["cod"] == 200:
            main = data["main"]
            weather = data["weather"][0]
            temperature = main["temp"]
            description = weather["description"]
            
            humidity = main["humidity"]
            wind_speed = data["wind"]["speed"]
            pressure = main["pressure"]
            visibility = data.get("visibility", "N/A")
            report = (
                f"Current weather in {city}:\n"
                f"- Condition: {description}\n"
                f"- Temperature: {temperature:.1f}°C\n"
                f"- Humidity: {humidity}%\n"
                f"- Pressure: {pressure} hPa\n"
                f"- Wind speed: {wind_speed} m/s\n"
                f"- Visibility: {visibility if isinstance(visibility, str) else visibility/1000:.1f} km"
            )
            return {"status": "success", "report": report}
        else:
            return {
                "status": "error",
                "error_message": f"Error fetching weather for '{city}' (queried as '{city_query}'): {data.get('message', 'Unknown error')}",
            }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_message": f"Network error or invalid city: {e}",
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"An unexpected error occurred: {e}",
        }


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """
    # Convert Chinese city names to Pinyin with capitalization
    city_query = city
    if any('\u4e00' <= char <= '\u9fff' for char in city):
        pinyin_parts = pinyin(city, style=Style.NORMAL)
        city_query = "".join([part[0].capitalize() for part in pinyin_parts])

    # Common city to timezone mappings
    city_timezones = {
        "Shanghai": "Asia/Shanghai",
        "Beijing": "Asia/Shanghai",
        "NewYork": "America/New_York",
        "London": "Europe/London",
        "Tokyo": "Asia/Tokyo",
        "Paris": "Europe/Paris",
        "Berlin": "Europe/Berlin",
        "Sydney": "Australia/Sydney"
    }

    tz_identifier = city_timezones.get(city_query)
    if not tz_identifier:
        return {
            "status": "error",
            "error_message": f"Sorry, I don't have timezone information for {city}."
        }

    try:
        tz = ZoneInfo(tz_identifier)
        now = datetime.datetime.now(tz)
        report = (
            f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
        )
        return {"status": "success", "report": report}
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error getting time for {city}: {str(e)}"
        }


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city."
    ),
    tools=[get_weather, get_current_time],
)