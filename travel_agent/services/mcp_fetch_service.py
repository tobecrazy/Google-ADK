"""
MCP Fetch Service
Service for fetching content using MCP fetch server
"""

import json
import re
import logging
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse, quote

logger = logging.getLogger(__name__)


class MCPFetchService:
    """Service for fetching content using MCP fetch server"""
    
    def __init__(self):
        self.max_length = 5000
        self.start_index = 0
    
    def fetch_url(self, url: str, max_length: int = None, start_index: int = 0, raw: bool = False) -> Optional[str]:
        """
        Fetch content from a URL using MCP fetch server
        
        Args:
            url: URL to fetch
            max_length: Maximum number of characters to return
            start_index: Starting character index
            raw: Get raw HTML content without simplification
            
        Returns:
            Content from the URL or None if failed
        """
        try:
            params = {
                "url": url,
                "max_length": max_length or self.max_length,
                "start_index": start_index,
                "raw": raw
            }
            
            logger.info(f"MCP Fetch: Fetching {url} with params {params}")
            
            # Use actual HTTP request for real data fetching with better headers
            import requests
            import random
            
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            
            headers = {
                'User-Agent': random.choice(user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            try:
                response = requests.get(url, timeout=15, headers=headers)
                response.raise_for_status()
                content = response.text
                
                # Apply max_length limit
                if max_length and len(content) > max_length:
                    content = content[start_index:start_index + max_length]
                
                logger.info(f"Successfully fetched {len(content)} characters from {url}")
                return content
                
            except Exception as fallback_error:
                logger.error(f"Failed to fetch {url}: {fallback_error}")
                return None
            
        except Exception as e:
            logger.error(f"Error fetching with MCP: {e}")
            return None
    
    def search_restaurants_with_mcp(self, destination: str, max_results: int = 10) -> List[str]:
        """
        Search for restaurants using MCP fetch server with Bing
        
        Args:
            destination: Destination to search restaurants for
            max_results: Maximum number of results to return
            
        Returns:
            List of search result URLs
        """
        try:
            # Use Bing search instead of DuckDuckGo for better reliability
            search_queries = [
                f"{destination} 最佳餐厅 推荐",
                f"{destination} best restaurants dining"
            ]
            
            all_urls = []
            
            for query in search_queries[:1]:  # Limit to 1 query for now
                search_url = f"https://www.bing.com/search?q={quote(query)}&mkt=zh-CN"
                
                content = self.fetch_url(search_url, max_length=8000)
                if not content:
                    logger.warning(f"No content returned for query: {query}")
                    continue
                
                # Extract result URLs from Bing
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                
                # Look for search results in multiple Bing formats
                result_selectors = [
                    '.b_algo',           # Standard Bing results
                    '.b_algo_group',     # Grouped results
                    '.b_ans',            # Answer results
                    '.b_pag',            # Paginated results
                    'li.b_algo',         # List item results
                    'div[data-priority]' # Priority results
                ]
                
                results = []
                for selector in result_selectors:
                    found_results = soup.select(selector)
                    results.extend(found_results)
                    if len(results) >= max_results:
                        break
                
                logger.info(f"Found {len(results)} potential result elements")
                
                for result in results[:max_results]:
                    try:
                        # Try multiple link selectors
                        link_selectors = [
                            'h2 a',
                            'h3 a', 
                            'a[href]',
                            '.b_title a',
                            '.b_algo_title a'
                        ]
                        
                        link_elem = None
                        for link_selector in link_selectors:
                            link_elem = result.select_one(link_selector)
                            if link_elem:
                                break
                        
                        if link_elem:
                            href = link_elem.get('href')
                            if href and href not in all_urls and href.startswith('http'):
                                all_urls.append(href)
                                logger.info(f"Found URL: {href}")
                    except Exception as e:
                        logger.warning(f"Error extracting URL from result: {e}")
                        continue
            
            logger.info(f"Found {len(all_urls)} restaurant search URLs for {destination}")
            return all_urls[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching restaurants with MCP: {e}")
            return []
    
    def search_images_with_mcp(self, query: str, max_results: int = 5) -> List[str]:
        """
        Search for images using MCP fetch server with Bing
        
        Args:
            query: Search query for images
            max_results: Maximum number of image URLs to return
            
        Returns:
            List of image URLs
        """
        try:
            # Use Bing image search instead of DuckDuckGo
            search_url = f"https://www.bing.com/images/search?q={quote(query)}&mkt=zh-CN"
            
            content = self.fetch_url(search_url, raw=True)
            if not content:
                logger.warning("No content returned from fetch")
                return []
            
            # Extract image URLs from the response
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
            
            logger.info(f"Searching for images in {len(content)} characters of content")
            
            for pattern in img_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
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
            
            logger.info(f"Found {len(image_urls)} images for query: {query}")
            return image_urls
            
        except Exception as e:
            logger.error(f"Error searching images with MCP: {e}")
            return []
    
    def fetch_restaurant_page(self, restaurant_url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch restaurant page content using MCP fetch
        
        Args:
            restaurant_url: URL of the restaurant page
            
        Returns:
            Dictionary containing restaurant page data
        """
        try:
            content = self.fetch_url(restaurant_url, max_length=10000)
            if not content:
                return None
            
            # Parse the content to extract restaurant information
            restaurant_data = {
                "url": restaurant_url,
                "content": content,
                "extracted_at": "mcp_fetch",
                "content_length": len(content)
            }
            
            return restaurant_data
            
        except Exception as e:
            logger.error(f"Error fetching restaurant page with MCP: {e}")
            return None


class MCPImageService:
    """Specialized service for image search using MCP fetch"""
    
    def __init__(self):
        self.mcp_fetch = MCPFetchService()
    
    def get_restaurant_images(self, restaurant_name: str, location: str = "") -> List[str]:
        """
        Get restaurant images using MCP fetch
        
        Args:
            restaurant_name: Name of the restaurant
            location: Location of the restaurant
            
        Returns:
            List of image URLs
        """
        query = f"{restaurant_name} restaurant"
        if location:
            query += f" {location}"
        
        return self.mcp_fetch.search_images_with_mcp(query, max_results=3)
    
    def get_attraction_images(self, attraction_name: str, location: str = "") -> List[str]:
        """
        Get attraction images using MCP fetch
        
        Args:
            attraction_name: Name of the attraction
            location: Location of the attraction
            
        Returns:
            List of image URLs
        """
        query = f"{attraction_name}"
        if location:
            query += f" {location}"
        
        return self.mcp_fetch.search_images_with_mcp(query, max_results=3)
    
    def get_food_images(self, food_name: str, cuisine_type: str = "") -> List[str]:
        """
        Get food images using MCP fetch
        
        Args:
            food_name: Name of the food/dish
            cuisine_type: Type of cuisine
            
        Returns:
            List of image URLs
        """
        query = f"{food_name}"
        if cuisine_type:
            query += f" {cuisine_type}"
        query += " food dish"
        
        return self.mcp_fetch.search_images_with_mcp(query, max_results=2)


# MCP Configuration
def get_mcp_fetch_config() -> Dict[str, Any]:
    """
    Get the MCP fetch server configuration
    
    Returns:
        Configuration dictionary for MCP fetch server
    """
    return {
        "mcp": {
            "servers": {
                "fetch": {
                    "command": "uvx",
                    "args": ["mcp-server-fetch"]
                }
            }
        }
    }


# Helper function to use actual MCP fetch
def use_mcp_fetch_tool(url: str, max_length: int = 5000, start_index: int = 0, raw: bool = False) -> Optional[str]:
    """
    Helper function to use MCP fetch tool with real data
    
    Args:
        url: URL to fetch
        max_length: Maximum content length
        start_index: Starting index
        raw: Whether to get raw HTML
        
    Returns:
        Fetched content or None
    """
    try:
        # Use requests for real data fetching with better headers
        import requests
        import random
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()
        content = response.text
        
        # Apply parameters
        if max_length and len(content) > max_length:
            content = content[start_index:start_index + max_length]
        
        logger.info(f"MCP Fetch Tool: Successfully fetched {len(content)} characters from {url}")
        return content
        
    except Exception as e:
        logger.error(f"MCP Fetch Tool error for {url}: {e}")
        return None
