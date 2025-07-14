import requests
from bs4 import BeautifulSoup
from ..config.settings import USER_AGENTS, REQUEST_INTERVAL
import time

class WebCrawler:
    def __init__(self, google_web_search_tool):
        self.google_web_search = google_web_search_tool

    def get_attractions(self, city: str, max_attractions=5):
        """Searches for top attractions in a city."""
        print(f"Searching for attractions in {city}...")
        try:
            search_results = self.google_web_search(query=f"top attractions in {city}")
            attractions = []
            for result in search_results.get("results", [])[:max_attractions]:
                attractions.append({
                    "name": result.get("title"),
                    "description": result.get("snippet"),
                    "image_url": self.get_image_url(result.get("title"))
                })
                time.sleep(REQUEST_INTERVAL) # Respect request interval
            return attractions
        except Exception as e:
            print(f"Error while searching for attractions: {e}")
            return []

    def get_image_url(self, query: str):
        """Searches for an image URL for a given query."""
        print(f"Searching for image: {query}")
        try:
            # This is a placeholder for a real image search
            # In a real implementation, we would use an image search API
            return f"https://via.placeholder.com/300x200.png?text={query.replace(' ', '+')}"
        except Exception as e:
            print(f"Error while searching for image: {e}")
            return ""
