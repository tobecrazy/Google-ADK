"""
Bing Search Utilities
Unified utilities for Bing search operations to eliminate code duplication
"""

import logging
import time
import random
import re
from typing import Dict, Any, List, Optional
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger(__name__)


class BingSearchUtils:
    """Unified Bing search utilities to eliminate code duplication"""
    
    def __init__(self):
        """Initialize Bing search utilities"""
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        self._setup_session()
    
    def _setup_session(self):
        """Setup requests session with optimal headers"""
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
    
    def build_search_url(self, query: str, search_type: str = 'web', market: str = 'zh-CN') -> str:
        """
        Build Bing search URL
        
        Args:
            query: Search query
            search_type: Type of search ('web', 'images')
            market: Market locale
            
        Returns:
            Formatted Bing search URL
        """
        encoded_query = quote(query)
        
        if search_type == 'images':
            return f"https://www.bing.com/images/search?q={encoded_query}&mkt={market}"
        else:
            return f"https://www.bing.com/search?q={encoded_query}&mkt={market}"
    
    def perform_search(self, query: str, search_type: str = 'web', market: str = 'zh-CN', 
                      max_length: int = 8000, delay_range: tuple = (2, 4)) -> Optional[str]:
        """
        Perform Bing search and return HTML content
        
        Args:
            query: Search query
            search_type: Type of search ('web', 'images')
            market: Market locale
            max_length: Maximum content length
            delay_range: Random delay range in seconds
            
        Returns:
            HTML content or None if failed
        """
        try:
            search_url = self.build_search_url(query, search_type, market)
            
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(*delay_range))
            
            # Rotate user agent
            self.session.headers['User-Agent'] = random.choice(self.user_agents)
            
            logger.info(f"Performing Bing {search_type} search: {query}")
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            content = response.text
            if max_length and len(content) > max_length:
                content = content[:max_length]
            
            logger.info(f"Successfully fetched {len(content)} characters from Bing")
            return content
            
        except Exception as e:
            logger.error(f"Error performing Bing search for '{query}': {str(e)}")
            return None
    
    def parse_web_results(self, html_content: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Parse Bing web search results
        
        Args:
            html_content: HTML content from Bing search
            max_results: Maximum number of results to return
            
        Returns:
            List of parsed search results
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Bing web search result selectors
            result_selectors = [
                '.b_algo',
                '.b_algo_group',
                '.b_ans',
                '.b_result'
            ]
            
            results = []
            for selector in result_selectors:
                results = soup.select(selector)
                if results:
                    break
            
            parsed_results = []
            for result in results[:max_results]:
                try:
                    parsed_result = self._parse_single_web_result(result)
                    if parsed_result:
                        parsed_results.append(parsed_result)
                except Exception as e:
                    logger.warning(f"Error parsing single web result: {str(e)}")
                    continue
            
            logger.info(f"Parsed {len(parsed_results)} web results from Bing")
            return parsed_results
            
        except Exception as e:
            logger.error(f"Error parsing Bing web results: {str(e)}")
            return []
    
    def _parse_single_web_result(self, result_element) -> Optional[Dict[str, Any]]:
        """Parse a single Bing web search result"""
        try:
            # Extract title and description using Bing-specific selectors
            title_elem = result_element.select_one('h2 a, .b_title a, .b_algo h2 a')
            desc_elem = result_element.select_one('.b_caption p, .b_snippet, .b_descript')
            url_elem = result_element.select_one('h2 a, .b_title a, .b_algo h2 a')
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            url = url_elem.get('href') if url_elem else ''
            
            return {
                'title': title,
                'description': description,
                'url': url,
                'source': 'bing_search'
            }
            
        except Exception as e:
            logger.warning(f"Error parsing single Bing result: {str(e)}")
            return None
    
    def parse_restaurant_results(self, html_content: str, destination: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Parse Bing search results specifically for restaurant information
        
        Args:
            html_content: HTML content from Bing search
            destination: Destination location
            max_results: Maximum number of results to return
            
        Returns:
            List of parsed restaurant results
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Bing web search result selectors
            result_selectors = [
                '.b_algo',
                '.b_algo_group',
                '.b_ans',
                '.b_result'
            ]
            
            results = []
            for selector in result_selectors:
                results = soup.select(selector)
                if results:
                    break
            
            restaurants = []
            for result in results[:max_results]:
                try:
                    restaurant = self._parse_single_restaurant_result(result, destination)
                    if restaurant:
                        restaurants.append(restaurant)
                except Exception as e:
                    logger.warning(f"Error parsing restaurant result: {str(e)}")
                    continue
            
            logger.info(f"Parsed {len(restaurants)} restaurant results from Bing")
            return restaurants
            
        except Exception as e:
            logger.error(f"Error parsing Bing restaurant results: {str(e)}")
            return []
    
    def _parse_single_restaurant_result(self, element, destination: str) -> Optional[Dict[str, Any]]:
        """Parse a single Bing search result for restaurant information"""
        try:
            # Extract title and description
            title_elem = element.select_one('h2 a, .b_title a, .b_algo h2 a')
            desc_elem = element.select_one('.b_caption p, .b_snippet, .b_descript')
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            # Filter for restaurant-related results
            restaurant_indicators = [
                '餐厅', '饭店', '酒楼', '茶餐厅', '火锅', '川菜', '粤菜', '湘菜',
                'restaurant', 'dining', 'food', 'cuisine', 'cafe', 'bar', 'bistro',
                '美食', '小吃', '菜', '料理', '烧烤', '麻辣烫'
            ]
            
            if not any(indicator in title.lower() or indicator in description.lower() 
                      for indicator in restaurant_indicators):
                return None
            
            # Extract potential restaurant name from title
            name = re.sub(r'^.*?[：:]\s*', '', title)  # Remove "destination: " prefix
            name = re.sub(r'\s*[-–—]\s*.*$', '', name)  # Remove " - description" suffix
            name = re.sub(r'\s*\|\s*.*$', '', name)    # Remove " | site" suffix
            name = re.sub(r'\s*\.\.\.$', '', name)     # Remove trailing dots
            
            if len(name) < 3:
                return None
            
            # Determine cuisine type from description and title
            cuisine = self._determine_cuisine(title + ' ' + description)
            
            # Extract rating if mentioned
            rating = self._extract_rating(description)
            
            # Determine price range from description
            price_range = self._determine_price_range(title + ' ' + description)
            
            return {
                'name': name[:50],  # Limit name length
                'description': description[:200],  # Limit description length
                'cuisine': cuisine,
                'rating': min(max(rating, 1.0), 5.0),  # Ensure rating is between 1-5
                'price_range': price_range,
                'specialties': [cuisine + ' cuisine'],
                'location': destination,
                'review_count': 0,  # Not available from search results
                'source': 'bing_search',
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Error parsing Bing restaurant result: {str(e)}")
            return None
    
    def _determine_cuisine(self, text: str) -> str:
        """Determine cuisine type from text"""
        cuisine_mapping = {
            '川菜': 'Sichuan',
            '粤菜': 'Cantonese', 
            '湘菜': 'Hunan',
            '东北菜': 'Northeastern',
            '西餐': 'Western',
            '日料': 'Japanese',
            '韩料': 'Korean',
            '泰菜': 'Thai',
            '意大利': 'Italian',
            '法餐': 'French',
            '印度': 'Indian',
            '火锅': 'Hot Pot',
            '烧烤': 'BBQ',
            '海鲜': 'Seafood'
        }
        
        text_lower = text.lower()
        for keyword, cuisine_type in cuisine_mapping.items():
            if keyword in text_lower:
                return cuisine_type
        
        return 'Local'
    
    def _extract_rating(self, text: str) -> float:
        """Extract rating from text"""
        rating_patterns = [
            r'(\d+\.?\d*)\s*分',
            r'(\d+\.?\d*)\s*星',
            r'rating[:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)/5'
        ]
        
        for pattern in rating_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    rating = float(match.group(1))
                    if rating > 5:  # Assume it's out of 10, convert to 5
                        rating = rating / 2
                    return rating
                except ValueError:
                    continue
        
        return 4.0  # Default rating
    
    def _determine_price_range(self, text: str) -> str:
        """Determine price range from text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['高端', '豪华', 'luxury', 'fine dining', 'expensive']):
            return 'High-end'
        elif any(word in text_lower for word in ['便宜', '实惠', 'cheap', 'budget', 'affordable']):
            return 'Budget'
        elif any(word in text_lower for word in ['奢华', 'michelin', '米其林']):
            return 'Luxury'
        
        return 'Mid-range'
    
    def parse_image_results(self, html_content: str, max_results: int = 5) -> List[str]:
        """
        Parse Bing image search results
        
        Args:
            html_content: HTML content from Bing image search
            max_results: Maximum number of image URLs to return
            
        Returns:
            List of image URLs
        """
        try:
            image_urls = []
            
            # Look for image URLs in Bing image search results
            img_patterns = [
                r'"murl":"([^"]+)"',                    # Main image URL
                r'"imgurl":"([^"]+)"',                  # Image URL
                r'"src":"([^"]+\.(?:jpg|jpeg|png|gif|webp))"',  # Source attribute
                r'data-src="([^"]+\.(?:jpg|jpeg|png|gif|webp))"',  # Data source
                r'"turl":"([^"]+)"',                    # Thumbnail URL
                r'imgurl=([^&]+)',                      # URL parameter
                r'src="([^"]+\.(?:jpg|jpeg|png|gif|webp))"'  # Direct src
            ]
            
            logger.info(f"Searching for images in {len(html_content)} characters of content")
            
            for pattern in img_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    if len(image_urls) >= max_results:
                        break
                    
                    # Clean up the URL
                    img_url = match.replace('\\/', '/')
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif not img_url.startswith(('http://', 'https://')):
                        continue
                    
                    if img_url not in image_urls:
                        image_urls.append(img_url)
                
                if len(image_urls) >= max_results:
                    break
            
            logger.info(f"Found {len(image_urls)} images from Bing")
            return image_urls
            
        except Exception as e:
            logger.error(f"Error parsing Bing image results: {str(e)}")
            return []
    
    def search_restaurants(self, destination: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Unified method to search for restaurants using Bing
        
        Args:
            destination: Destination to search restaurants for
            max_results: Maximum number of results to return
            
        Returns:
            List of restaurant data
        """
        try:
            restaurants = []
            
            # Search queries for different types of restaurants
            search_queries = [
                f"{destination} 最佳餐厅 推荐",
                f"{destination} best restaurants dining"
            ]
            
            for query in search_queries:
                try:
                    content = self.perform_search(query, 'web', 'zh-CN', 8000)
                    if content:
                        query_restaurants = self.parse_restaurant_results(content, destination, max_results // len(search_queries))
                        restaurants.extend(query_restaurants)
                        
                        # Add delay between queries
                        time.sleep(random.uniform(2, 3))
                        
                except Exception as e:
                    logger.warning(f"Error with restaurant search query '{query}': {str(e)}")
                    continue
            
            return restaurants[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching restaurants: {str(e)}")
            return []
    
    def search_images(self, query: str, max_results: int = 5) -> List[str]:
        """
        Unified method to search for images using Bing
        
        Args:
            query: Search query for images
            max_results: Maximum number of image URLs to return
            
        Returns:
            List of image URLs
        """
        try:
            content = self.perform_search(query, 'images', 'zh-CN', 10000)
            if content:
                return self.parse_image_results(content, max_results)
            return []
            
        except Exception as e:
            logger.error(f"Error searching images: {str(e)}")
            return []
    
    def close(self):
        """Close the session"""
        try:
            if self.session:
                self.session.close()
            logger.info("Bing search utils session closed")
        except Exception as e:
            logger.error(f"Error closing Bing search utils session: {str(e)}")


# Global instance for reuse
_bing_search_utils = None

def get_bing_search_utils() -> BingSearchUtils:
    """Get global Bing search utils instance"""
    global _bing_search_utils
    if _bing_search_utils is None:
        _bing_search_utils = BingSearchUtils()
    return _bing_search_utils
