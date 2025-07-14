import requests
from ..config.settings import OPENWEATHER_API_KEY

class WeatherService:
    def get_weather(self, city: str) -> dict:
        """Retrieves the current weather report for a specified city."""
        if not OPENWEATHER_API_KEY:
            return {
                "status": "error",
                "error_message": "OpenWeather API key is not set.",
            }

        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = f"{base_url}q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        
        try:
            response = requests.get(complete_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error_message": f"Network error or invalid city: {e}",
            }