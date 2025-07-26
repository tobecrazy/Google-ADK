"""
Web Scraper Utility
Provides web scraping capabilities with anti-detection measures
"""

import os
import logging
import time
import random
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

class WebScraper:
    """Web scraping utility with anti-detection features."""
    
    def __init__(self):
        """Initialize the web scraper."""
        self.session = requests.Session()
        self.driver = None
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        logger.info("Web Scraper initialized")
    
    def scrape_url(self, url: str, use_selenium: bool = False) -> Optional[Dict[str, Any]]:
        """
        Scrape content from a URL.
        
        Args:
            url: URL to scrape
            use_selenium: Whether to use Selenium for JavaScript-heavy sites
            
        Returns:
            Dict containing scraped data or None if failed
        """
        try:
            if use_selenium:
                return self._scrape_with_selenium(url)
            else:
                return self._scrape_with_requests(url)
                
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            return None
    
    def _scrape_with_requests(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape using requests library."""
        try:
            # Rotate user agent
            self.session.headers['User-Agent'] = random.choice(self.user_agents)
            
            # Add random delay to avoid being blocked
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            return {
                'success': True,
                'url': url,
                'title': soup.title.string if soup.title else '',
                'content': soup.get_text(strip=True),
                'html': str(soup),
                'status_code': response.status_code,
                'method': 'requests'
            }
            
        except Exception as e:
            logger.error(f"Error scraping with requests: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'method': 'requests'
            }
    
    def _scrape_with_selenium(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape using Selenium for JavaScript-heavy sites."""
        try:
            if not self.driver:
                self._setup_selenium_driver()
            
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page content
            title = self.driver.title
            content = self.driver.find_element(By.TAG_NAME, "body").text
            html = self.driver.page_source
            
            return {
                'success': True,
                'url': url,
                'title': title,
                'content': content,
                'html': html,
                'method': 'selenium'
            }
            
        except Exception as e:
            logger.error(f"Error scraping with Selenium: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'method': 'selenium'
            }
    
    def _setup_selenium_driver(self):
        """Setup Selenium Chrome driver with options."""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument(f'--user-agent={random.choice(self.user_agents)}')
            
            # Install and setup ChromeDriver
            self.driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            logger.info("Selenium driver setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up Selenium driver: {str(e)}")
            self.driver = None
    
    def scrape_travel_data(self, destination: str) -> Dict[str, Any]:
        """
        Scrape travel-related data for a destination.
        
        Args:
            destination: Destination to search for
            
        Returns:
            Dict containing scraped travel data
        """
        try:
            # This is a placeholder implementation
            # In a real scenario, you would scrape from specific travel websites
            
            search_queries = [
                f"{destination} attractions",
                f"{destination} hotels",
                f"{destination} restaurants",
                f"{destination} travel guide"
            ]
            
            scraped_data = {
                'destination': destination,
                'attractions': [],
                'hotels': [],
                'restaurants': [],
                'general_info': '',
                'sources': []
            }
            
            # Simulate scraping (in reality, you'd scrape actual travel sites)
            for query in search_queries:
                # Add simulated data
                if 'attractions' in query:
                    scraped_data['attractions'].extend([
                        f"{destination} Historic Center",
                        f"{destination} Museum",
                        f"{destination} Park"
                    ])
                elif 'hotels' in query:
                    scraped_data['hotels'].extend([
                        f"{destination} Grand Hotel",
                        f"{destination} Budget Inn",
                        f"{destination} Boutique Hotel"
                    ])
                elif 'restaurants' in query:
                    scraped_data['restaurants'].extend([
                        f"{destination} Traditional Restaurant",
                        f"{destination} Street Food Market",
                        f"{destination} Fine Dining"
                    ])
            
            scraped_data['general_info'] = f"Travel information for {destination} compiled from various sources."
            
            return {
                'success': True,
                'data': scraped_data,
                'note': 'This is simulated data. In production, implement actual web scraping.'
            }
            
        except Exception as e:
            logger.error(f"Error scraping travel data: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def extract_structured_data(self, html_content: str, data_type: str) -> List[Dict[str, Any]]:
        """
        Extract structured data from HTML content.
        
        Args:
            html_content: HTML content to parse
            data_type: Type of data to extract (attractions, hotels, restaurants)
            
        Returns:
            List of extracted structured data
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            extracted_data = []
            
            if data_type == 'attractions':
                # Look for common attraction listing patterns
                attraction_selectors = [
                    '.attraction-item',
                    '.poi-item',
                    '.listing-item',
                    '[data-testid*="attraction"]'
                ]
                
                for selector in attraction_selectors:
                    items = soup.select(selector)
                    for item in items[:10]:  # Limit to 10 items
                        name = self._extract_text(item, ['h1', 'h2', 'h3', '.name', '.title'])
                        description = self._extract_text(item, ['.description', '.summary', 'p'])
                        rating = self._extract_rating(item)
                        
                        if name:
                            extracted_data.append({
                                'name': name,
                                'description': description,
                                'rating': rating,
                                'type': 'attraction'
                            })
            
            elif data_type == 'hotels':
                # Look for hotel listing patterns
                hotel_selectors = [
                    '.hotel-item',
                    '.accommodation-item',
                    '.property-item'
                ]
                
                for selector in hotel_selectors:
                    items = soup.select(selector)
                    for item in items[:10]:
                        name = self._extract_text(item, ['h1', 'h2', 'h3', '.name', '.title'])
                        price = self._extract_price(item)
                        rating = self._extract_rating(item)
                        
                        if name:
                            extracted_data.append({
                                'name': name,
                                'price': price,
                                'rating': rating,
                                'type': 'hotel'
                            })
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error extracting structured {str(e)}")
            return []
    
    def _extract_text(self, element, selectors: List[str]) -> str:
        """Extract text from element using multiple selectors."""
        for selector in selectors:
            found = element.select_one(selector)
            if found and found.get_text(strip=True):
                return found.get_text(strip=True)
        return ''
    
    def _extract_rating(self, element) -> Optional[float]:
        """Extract rating from element."""
        rating_selectors = ['.rating', '.score', '[data-rating]', '.stars']
        
        for selector in rating_selectors:
            rating_elem = element.select_one(selector)
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                # Try to extract numeric rating
                import re
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    return float(rating_match.group(1))
        
        return None
    
    def _extract_price(self, element) -> Optional[str]:
        """Extract price from element."""
        price_selectors = ['.price', '.cost', '.rate', '[data-price]']
        
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                return price_elem.get_text(strip=True)
        
        return None
    
    def close(self):
        """Close the web scraper and cleanup resources."""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
            
            if self.session:
                self.session.close()
            
            logger.info("Web scraper closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing web scraper: {str(e)}")
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.close()
