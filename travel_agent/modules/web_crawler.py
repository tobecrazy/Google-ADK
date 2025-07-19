import requests
from bs4 import BeautifulSoup
import time
import random
from ..config.settings import USER_AGENTS, REQUEST_INTERVAL


class WebCrawler:
    def get_attractions(self, city: str, max_attractions=5):
        """Searches for top attractions in a city."""
        print(f"Searching for attractions in {city}...")
        attractions = []
        try:
            search_query = f"top attractions in {city}"
            search_results = self.google_web_search(query=search_query)
            
            # Parse search results to extract attraction names and descriptions
            # This is a simplified parsing, a more robust solution might be needed
            for result in search_results.get('search_results', [])[:max_attractions]:
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                link = result.get('link', '')

                if title and snippet:
                    image_url = self.get_image_url(title)
                    attractions.append({
                        "name": title,
                        "description": snippet,
                        "image_url": image_url
                    })
                    time.sleep(REQUEST_INTERVAL) # Be respectful of API limits and website policies
            return attractions
        except Exception as e:
            print(f"Error while searching for attractions: {e}")
            return []

    def get_image_url(self, query: str):
        """Searches for an image URL for a given query."""
        print(f"Searching for image: {query}")
        try:
            image_search_query = f"{query} image"
            image_search_results = google_web_search(query=image_search_query)
            
            # Look for an image URL in the search results
            for result in image_search_results.get('search_results', []):
                if 'thumbnail' in result and result['thumbnail'] and 'url' in result['thumbnail']:
                    return result['thumbnail']['url']
            return "" # Return empty string if no image found
        except Exception as e:
            print(f"Error while searching for image: {e}")
            return ""