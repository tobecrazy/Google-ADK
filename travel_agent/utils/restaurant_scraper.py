"""
Restaurant Web Scraper
Specialized web scraper for collecting restaurant data from multiple sources
"""

import os
import logging
import time
import random
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re
import json
from urllib.parse import urljoin, urlparse, quote
from datetime import datetime

logger = logging.getLogger(__name__)

class RestaurantScraper:
    """Specialized scraper for restaurant data from multiple sources."""
    
    def __init__(self):
        """Initialize the restaurant scraper."""
        self.session = requests.Session()
        self.driver = None
        
        # Enhanced user agents for better success rate
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Restaurant-specific search patterns
        self.restaurant_keywords = {
            'chinese': ['餐厅', '饭店', '酒楼', '茶餐厅', '火锅', '川菜', '粤菜', '湘菜', '东北菜'],
            'international': ['西餐', '日料', '韩料', '泰菜', '意大利菜', '法餐', '印度菜'],
            'casual': ['小吃', '快餐', '咖啡厅', '茶馆', '甜品店', '烧烤', '麻辣烫'],
            'specialty': ['海鲜', '素食', '清真', '烘焙', '酒吧', '夜宵']
        }
        
        # Configure session with better headers
        self._setup_session()
        
        logger.info("Restaurant Scraper initialized")
    
    def _setup_session(self):
        """Setup requests session with optimal headers."""
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
    
    def scrape_restaurants_multi_source(
        self, 
        destination: str, 
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Scrape restaurants from multiple sources.
        
        Args:
            destination: Target destination
            max_results: Maximum number of results to return
            
        Returns:
            List of restaurant data from multiple sources
        """
        try:
            logger.info(f"Starting multi-source restaurant scraping for {destination}")
            
            all_restaurants = []
            
            # Source 1: TripAdvisor (International coverage)
            try:
                tripadvisor_restaurants = self._scrape_tripadvisor(destination, max_results // 4)
                all_restaurants.extend(tripadvisor_restaurants)
                logger.info(f"Found {len(tripadvisor_restaurants)} restaurants from TripAdvisor")
            except Exception as e:
                logger.warning(f"TripAdvisor scraping failed: {str(e)}")
            
            # Source 2: Generic search engines for restaurant listings
            try:
                search_restaurants = self._scrape_search_engines(destination, max_results // 4)
                all_restaurants.extend(search_restaurants)
                logger.info(f"Found {len(search_restaurants)} restaurants from search engines")
            except Exception as e:
                logger.warning(f"Search engine scraping failed: {str(e)}")
            
            # Source 3: Local tourism websites
            try:
                tourism_restaurants = self._scrape_tourism_sites(destination, max_results // 4)
                all_restaurants.extend(tourism_restaurants)
                logger.info(f"Found {len(tourism_restaurants)} restaurants from tourism sites")
            except Exception as e:
                logger.warning(f"Tourism site scraping failed: {str(e)}")
            
            # Source 4: Food blogs and review sites
            try:
                blog_restaurants = self._scrape_food_blogs(destination, max_results // 4)
                all_restaurants.extend(blog_restaurants)
                logger.info(f"Found {len(blog_restaurants)} restaurants from food blogs")
            except Exception as e:
                logger.warning(f"Food blog scraping failed: {str(e)}")
            
            # Deduplicate and enhance results
            unique_restaurants = self._deduplicate_restaurants(all_restaurants)
            enhanced_restaurants = self._enhance_restaurant_data(unique_restaurants, destination)
            
            # Sort by quality score and return top results
            final_restaurants = sorted(
                enhanced_restaurants, 
                key=lambda x: x.get('quality_score', 0), 
                reverse=True
            )[:max_results]
            
            logger.info(f"Successfully scraped {len(final_restaurants)} unique restaurants")
            return final_restaurants
            
        except Exception as e:
            logger.error(f"Error in multi-source restaurant scraping: {str(e)}")
            return []
    
    def _scrape_tripadvisor(self, destination: str, max_results: int) -> List[Dict[str, Any]]:
        """Scrape restaurants from TripAdvisor."""
        try:
            restaurants = []
            
            # TripAdvisor search URL
            search_query = f"{destination} restaurants"
            search_url = f"https://www.tripadvisor.com/Search?q={quote(search_query)}"
            
            # Add delay to avoid rate limiting
            time.sleep(random.uniform(2, 4))
            
            # Rotate user agent
            self.session.headers['User-Agent'] = random.choice(self.user_agents)
            
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for restaurant listings
            restaurant_selectors = [
                '[data-test-target="restaurants-list"] [data-test-target="restaurant-card"]',
                '.restaurant-card',
                '.listing-card',
                '[class*="restaurant"]'
            ]
            
            for selector in restaurant_selectors:
                restaurant_elements = soup.select(selector)
                if restaurant_elements:
                    break
            
            for element in restaurant_elements[:max_results]:
                try:
                    restaurant = self._parse_tripadvisor_restaurant(element)
                    if restaurant:
                        restaurant['source'] = 'tripadvisor'
                        restaurant['scraped_at'] = datetime.now().isoformat()
                        restaurants.append(restaurant)
                except Exception as e:
                    logger.warning(f"Error parsing TripAdvisor restaurant: {str(e)}")
                    continue
            
            return restaurants
            
        except Exception as e:
            logger.error(f"Error scraping TripAdvisor: {str(e)}")
            return []
    
    def _parse_tripadvisor_restaurant(self, element) -> Optional[Dict[str, Any]]:
        """Parse a TripAdvisor restaurant element."""
        try:
            # Extract name
            name_selectors = ['h3', '.restaurant-name', '[data-test-target="restaurant-name"]', 'a[href*="Restaurant"]']
            name = ''
            for selector in name_selectors:
                name_elem = element.select_one(selector)
                if name_elem and name_elem.get_text(strip=True):
                    name = name_elem.get_text(strip=True)
                    break
            
            if not name or len(name) < 2:
                return None
            
            # Extract rating
            rating = None
            rating_selectors = ['.rating', '[class*="rating"]', '[data-test-target="review-rating"]']
            for selector in rating_selectors:
                rating_elem = element.select_one(selector)
                if rating_elem:
                    rating_text = rating_elem.get('aria-label', '') or rating_elem.get_text()
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        rating = float(rating_match.group(1))
                        break
            
            # Extract cuisine type
            cuisine = ''
            cuisine_selectors = ['.cuisine', '[class*="cuisine"]', '.category']
            for selector in cuisine_selectors:
                cuisine_elem = element.select_one(selector)
                if cuisine_elem:
                    cuisine = cuisine_elem.get_text(strip=True)
                    break
            
            # Extract price range
            price_range = ''
            price_selectors = ['.price', '[class*="price"]', '.cost']
            for selector in price_selectors:
                price_elem = element.select_one(selector)
                if price_elem:
                    price_range = price_elem.get_text(strip=True)
                    break
            
            # Extract review count
            review_count = 0
            review_selectors = ['.review-count', '[class*="review"]']
            for selector in review_selectors:
                review_elem = element.select_one(selector)
                if review_elem:
                    review_text = review_elem.get_text()
                    review_match = re.search(r'(\d+)', review_text)
                    if review_match:
                        review_count = int(review_match.group(1))
                        break
            
            return {
                'name': name,
                'rating': rating or 4.0,
                'cuisine': cuisine or 'International',
                'price_range': price_range or 'Mid-range',
                'review_count': review_count,
                'description': f'Popular restaurant in the area with good reviews.',
                'specialties': [cuisine] if cuisine else ['International cuisine']
            }
            
        except Exception as e:
            logger.warning(f"Error parsing TripAdvisor restaurant element: {str(e)}")
            return None
    
    def _scrape_search_engines(self, destination: str, max_results: int) -> List[Dict[str, Any]]:
        """Scrape restaurant data from search engine results."""
        try:
            restaurants = []
            
            # Search queries for different types of restaurants
            search_queries = [
                f"{destination} 最佳餐厅",
                f"{destination} 推荐美食",
                f"{destination} 特色餐厅",
                f"{destination} best restaurants"
            ]
            
            for query in search_queries[:2]:  # Limit to 2 queries to avoid rate limiting
                try:
                    # Use DuckDuckGo as it's more scraping-friendly
                    search_url = f"https://duckduckgo.com/html/?q={quote(query)}"
                    
                    time.sleep(random.uniform(3, 5))
                    self.session.headers['User-Agent'] = random.choice(self.user_agents)
                    
                    response = self.session.get(search_url, timeout=15)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract search results
                    result_selectors = ['.result', '.web-result', '.result__body']
                    results = []
                    
                    for selector in result_selectors:
                        results = soup.select(selector)
                        if results:
                            break
                    
                    for result in results[:max_results//2]:
                        try:
                            restaurant = self._parse_search_result(result, destination)
                            if restaurant:
                                restaurant['source'] = 'search_engine'
                                restaurant['scraped_at'] = datetime.now().isoformat()
                                restaurants.append(restaurant)
                        except Exception as e:
                            logger.warning(f"Error parsing search result: {str(e)}")
                            continue
                            
                except Exception as e:
                    logger.warning(f"Error with search query '{query}': {str(e)}")
                    continue
            
            return restaurants
            
        except Exception as e:
            logger.error(f"Error scraping search engines: {str(e)}")
            return []
    
    def _parse_search_result(self, result_element, destination: str) -> Optional[Dict[str, Any]]:
        """Parse a search engine result for restaurant information."""
        try:
            # Extract title and description
            title_elem = result_element.select_one('.result__title a, .result__a, h3 a, h2 a')
            desc_elem = result_element.select_one('.result__snippet, .snippet, .description')
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            # Filter for restaurant-related results
            restaurant_indicators = ['餐厅', '饭店', '美食', 'restaurant', 'dining', 'food', '菜', '料理']
            if not any(indicator in title.lower() or indicator in description.lower() 
                      for indicator in restaurant_indicators):
                return None
            
            # Extract potential restaurant name from title
            # Remove common prefixes/suffixes
            name = re.sub(r'^.*?[：:]\s*', '', title)  # Remove "destination: " prefix
            name = re.sub(r'\s*[-–—]\s*.*$', '', name)  # Remove " - description" suffix
            name = re.sub(r'\s*\|\s*.*$', '', name)    # Remove " | site" suffix
            
            if len(name) < 3:
                return None
            
            # Determine cuisine type from description
            cuisine = 'Local'
            for category, keywords in self.restaurant_keywords.items():
                if any(keyword in description for keyword in keywords):
                    cuisine = category.title()
                    break
            
            return {
                'name': name[:50],  # Limit name length
                'description': description[:200],  # Limit description length
                'cuisine': cuisine,
                'rating': 4.0,  # Default rating
                'price_range': 'Mid-range',
                'specialties': [cuisine + ' cuisine'],
                'location': destination
            }
            
        except Exception as e:
            logger.warning(f"Error parsing search result: {str(e)}")
            return None
    
    def _scrape_tourism_sites(self, destination: str, max_results: int) -> List[Dict[str, Any]]:
        """Scrape restaurant data from tourism websites."""
        try:
            restaurants = []
            
            # Common tourism website patterns
            tourism_queries = [
                f"{destination} tourism restaurants",
                f"{destination} travel guide dining",
                f"{destination} visitor guide food"
            ]
            
            for query in tourism_queries[:1]:  # Limit to 1 query
                try:
                    # Search for tourism sites
                    search_url = f"https://duckduckgo.com/html/?q={quote(query + ' site:gov.cn OR site:travel OR site:tourism')}"
                    
                    time.sleep(random.uniform(4, 6))
                    self.session.headers['User-Agent'] = random.choice(self.user_agents)
                    
                    response = self.session.get(search_url, timeout=15)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for tourism-related results
                    results = soup.select('.result')
                    
                    for result in results[:3]:  # Check top 3 results
                        try:
                            link_elem = result.select_one('.result__title a')
                            if link_elem:
                                url = link_elem.get('href')
                                if url and ('tourism' in url or 'travel' in url or 'gov.cn' in url):
                                    # Try to scrape the tourism page
                                    page_restaurants = self._scrape_tourism_page(url, destination, max_results//3)
                                    restaurants.extend(page_restaurants)
                        except Exception as e:
                            logger.warning(f"Error scraping tourism result: {str(e)}")
                            continue
                            
                except Exception as e:
                    logger.warning(f"Error with tourism query '{query}': {str(e)}")
                    continue
            
            return restaurants
            
        except Exception as e:
            logger.error(f"Error scraping tourism sites: {str(e)}")
            return []
    
    def _scrape_tourism_page(self, url: str, destination: str, max_results: int) -> List[Dict[str, Any]]:
        """Scrape a specific tourism page for restaurant information."""
        try:
            restaurants = []
            
            time.sleep(random.uniform(2, 4))
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for restaurant sections
            restaurant_sections = soup.find_all(text=re.compile(r'餐厅|美食|dining|restaurant', re.I))
            
            for section in restaurant_sections[:max_results]:
                try:
                    # Find the parent element containing restaurant info
                    parent = section.parent
                    if parent:
                        # Look for nearby restaurant names and descriptions
                        restaurant_info = self._extract_tourism_restaurant_info(parent, destination)
                        if restaurant_info:
                            restaurant_info['source'] = 'tourism_site'
                            restaurant_info['scraped_at'] = datetime.now().isoformat()
                            restaurants.append(restaurant_info)
                except Exception as e:
                    logger.warning(f"Error extracting tourism restaurant info: {str(e)}")
                    continue
            
            return restaurants
            
        except Exception as e:
            logger.warning(f"Error scraping tourism page {url}: {str(e)}")
            return []
    
    def _extract_tourism_restaurant_info(self, element, destination: str) -> Optional[Dict[str, Any]]:
        """Extract restaurant information from tourism page element."""
        try:
            # Get text content from element and nearby elements
            text_content = element.get_text(strip=True)
            
            # Look for restaurant names (usually in bold or headers)
            name_patterns = [
                r'([^。，,\n]{3,20}(?:餐厅|饭店|酒楼|restaurant))',
                r'([^。，,\n]{3,20}(?:菜|料理|cuisine))',
            ]
            
            name = ''
            for pattern in name_patterns:
                match = re.search(pattern, text_content, re.I)
                if match:
                    name = match.group(1).strip()
                    break
            
            if not name:
                # Fallback: use first substantial text as name
                words = text_content.split()
                if words and len(words[0]) > 2:
                    name = words[0][:30]
                else:
                    return None
            
            # Extract description
            description = text_content[:150] if len(text_content) > 20 else f"Popular restaurant in {destination}"
            
            return {
                'name': name,
                'description': description,
                'cuisine': 'Local',
                'rating': 4.2,
                'price_range': 'Mid-range',
                'specialties': ['Local specialties'],
                'location': destination
            }
            
        except Exception as e:
            logger.warning(f"Error extracting tourism restaurant info: {str(e)}")
            return None
    
    def _scrape_food_blogs(self, destination: str, max_results: int) -> List[Dict[str, Any]]:
        """Scrape restaurant data from food blogs and review sites."""
        try:
            restaurants = []
            
            # Food blog search queries
            blog_queries = [
                f"{destination} food blog recommendations",
                f"{destination} 美食博客 推荐",
                f"best {destination} restaurants blog"
            ]
            
            for query in blog_queries[:1]:  # Limit to 1 query
                try:
                    search_url = f"https://duckduckgo.com/html/?q={quote(query)}"
                    
                    time.sleep(random.uniform(3, 5))
                    self.session.headers['User-Agent'] = random.choice(self.user_agents)
                    
                    response = self.session.get(search_url, timeout=15)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    results = soup.select('.result')
                    
                    for result in results[:2]:  # Check top 2 results
                        try:
                            link_elem = result.select_one('.result__title a')
                            if link_elem:
                                url = link_elem.get('href')
                                if url and ('blog' in url or 'food' in url or '美食' in url):
                                    # Try to scrape the blog page
                                    blog_restaurants = self._scrape_blog_page(url, destination, max_results//2)
                                    restaurants.extend(blog_restaurants)
                        except Exception as e:
                            logger.warning(f"Error scraping blog result: {str(e)}")
                            continue
                            
                except Exception as e:
                    logger.warning(f"Error with blog query '{query}': {str(e)}")
                    continue
            
            return restaurants
            
        except Exception as e:
            logger.error(f"Error scraping food blogs: {str(e)}")
            return []
    
    def _scrape_blog_page(self, url: str, destination: str, max_results: int) -> List[Dict[str, Any]]:
        """Scrape a specific blog page for restaurant recommendations."""
        try:
            restaurants = []
            
            time.sleep(random.uniform(2, 4))
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for restaurant mentions in the blog content
            content_selectors = ['.content', '.post-content', '.article-content', 'article', '.entry-content']
            content = None
            
            for selector in content_selectors:
                content = soup.select_one(selector)
                if content:
                    break
            
            if not content:
                content = soup  # Fallback to entire page
            
            # Find restaurant names and descriptions
            text_content = content.get_text()
            
            # Look for restaurant patterns
            restaurant_patterns = [
                r'([^。，,\n]{3,30}(?:餐厅|饭店|酒楼|restaurant|cafe|bar))[^。，,\n]{0,100}',
                r'推荐[^。，,\n]*?([^。，,\n]{3,30})[^。，,\n]{0,100}',
            ]
            
            found_restaurants = set()  # Avoid duplicates
            
            for pattern in restaurant_patterns:
                matches = re.finditer(pattern, text_content, re.I)
                for match in matches:
                    if len(found_restaurants) >= max_results:
                        break
                    
                    restaurant_text = match.group(0)
                    restaurant_name = match.group(1).strip()
                    
                    if len(restaurant_name) > 2 and restaurant_name not in found_restaurants:
                        found_restaurants.add(restaurant_name)
                        
                        restaurant = {
                            'name': restaurant_name[:40],
                            'description': restaurant_text[:150],
                            'cuisine': 'Local',
                            'rating': 4.1,
                            'price_range': 'Mid-range',
                            'specialties': ['Blogger recommended'],
                            'location': destination,
                            'source': 'food_blog',
                            'scraped_at': datetime.now().isoformat()
                        }
                        restaurants.append(restaurant)
            
            return restaurants
            
        except Exception as e:
            logger.warning(f"Error scraping blog page {url}: {str(e)}")
            return []
    
    def _deduplicate_restaurants(self, restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate restaurants based on name similarity."""
        try:
            if not restaurants:
                return []
            
            unique_restaurants = []
            seen_names = set()
            
            for restaurant in restaurants:
                name = restaurant.get('name', '').strip().lower()
                
                # Clean name for comparison
                clean_name = re.sub(r'[^\w\s]', '', name)
                clean_name = re.sub(r'\s+', ' ', clean_name).strip()
                
                # Check for similar names
                is_duplicate = False
                for seen_name in seen_names:
                    # Simple similarity check
                    if (clean_name in seen_name or seen_name in clean_name or 
                        self._calculate_similarity(clean_name, seen_name) > 0.8):
                        is_duplicate = True
                        break
                
                if not is_duplicate and len(clean_name) > 2:
                    seen_names.add(clean_name)
                    unique_restaurants.append(restaurant)
            
            logger.info(f"Deduplicated {len(restaurants)} -> {len(unique_restaurants)} restaurants")
            return unique_restaurants
            
        except Exception as e:
            logger.error(f"Error deduplicating restaurants: {str(e)}")
            return restaurants
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings."""
        try:
            # Simple Jaccard similarity
            set1 = set(str1.split())
            set2 = set(str2.split())
            
            if not set1 and not set2:
                return 1.0
            if not set1 or not set2:
                return 0.0
            
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception:
            return 0.0
    
    def _enhance_restaurant_data(self, restaurants: List[Dict[str, Any]], destination: str) -> List[Dict[str, Any]]:
        """Enhance restaurant data with additional information and quality scoring."""
        try:
            enhanced_restaurants = []
            
            for restaurant in restaurants:
                try:
                    # Calculate quality score
                    quality_score = self._calculate_quality_score(restaurant)
                    restaurant['quality_score'] = quality_score
                    
                    # Enhance missing fields
                    if not restaurant.get('description'):
                        restaurant['description'] = f"Popular restaurant in {destination}"
                    
                    if not restaurant.get('specialties'):
                        cuisine = restaurant.get('cuisine', 'Local')
                        restaurant['specialties'] = [f"{cuisine} cuisine"]
                    
                    if not restaurant.get('price_range'):
                        restaurant['price_range'] = 'Mid-range'
                    
                    if not restaurant.get('rating'):
                        restaurant['rating'] = 4.0
                    
                    # Add estimated cost based on price range
                    price_mapping = {
                        'Budget': 30,
                        'Mid-range': 60,
                        'High-end': 120,
                        'Luxury': 200
                    }
                    
                    price_range = restaurant.get('price_range', 'Mid-range')
                    restaurant['estimated_cost'] = price_mapping.get(price_range, 60)
                    
                    # Add location if missing
                    if not restaurant.get('location'):
                        restaurant['location'] = destination
                    
                    enhanced_restaurants.append(restaurant)
                    
                except Exception as e:
                    logger.warning(f"Error enhancing restaurant {restaurant.get('name', 'Unknown')}: {str(e)}")
                    enhanced_restaurants.append(restaurant)  # Add without enhancement
            
            return enhanced_restaurants
            
        except Exception as e:
            logger.error(f"Error enhancing restaurant data: {str(e)}")
            return restaurants
    
    def _calculate_quality_score(self, restaurant: Dict[str, Any]) -> float:
        """Calculate a quality score for the restaurant based on available data."""
        try:
            score = 0.0
            
            # Name quality (0-20 points)
            name = restaurant.get('name', '')
            if len(name) > 2:
                score += 10
            if len(name) > 5:
                score += 5
            if not any(char.isdigit() for char in name):  # Prefer names without numbers
                score += 5
            
            # Description quality (0-15 points)
            description = restaurant.get('description', '')
            if len(description) > 20:
                score += 10
            if len(description) > 50:
                score += 5
            
            # Rating (0-25 points)
            rating = restaurant.get('rating', 0)
            if rating > 0:
                score += (rating / 5.0) * 25
            
            # Source reliability (0-20 points)
            source = restaurant.get('source', '')
            source_scores = {
                'tripadvisor': 20,
                'tourism_site': 15,
                'food_blog': 12,
                'search_engine': 8
            }
            score += source_scores.get(source, 5)
            
            # Data completeness (0-20 points)
            fields = ['cuisine', 'price_range', 'specialties', 'location']
            complete_fields = sum(1 for field in fields if restaurant.get(field))
            score += (complete_fields / len(fields)) * 20
            
            # Review count bonus (0-10 points)
            review_count = restaurant.get('review_count', 0)
            if review_count > 0:
                score += min(review_count / 100, 1.0) * 10
            
            return min(score, 100.0)  # Cap at 100 points
            
        except Exception as e:
            logger.warning(f"Error calculating quality score: {str(e)}")
            return 50.0  # Default score
    
    def close(self):
        """Close the scraper and cleanup resources."""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
            
            if self.session:
                self.session.close()
            
            logger.info("Restaurant scraper closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing restaurant scraper: {str(e)}")
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.close()
