"""
Restaurant Service
Provides real restaurant recommendations using Amap Maps API and other sources
"""

import os
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

logger = logging.getLogger(__name__)

class RestaurantService:
    """Service for real restaurant data using Amap and other sources."""
    
    def __init__(self, use_mcp_tool: Optional[Callable] = None):
        """Initialize the restaurant service with MCP tool access."""
        self.use_mcp_tool = use_mcp_tool
        
        # Initialize Gemini for data enhancement
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Restaurant categories for search
        self.restaurant_categories = [
            '餐厅', '中餐厅', '西餐厅', '火锅店', '烧烤店', 
            '小吃店', '咖啡厅', '茶餐厅', '日料', '韩料',
            '川菜', '粤菜', '湘菜', '东北菜', '海鲜'
        ]
        
        logger.info("Restaurant Service initialized with Amap integration")
    
    def get_restaurants(
        self,
        destination: str,
        budget: float,
        location_coords: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get real restaurant recommendations for the destination.
        
        Args:
            destination: Target destination
            budget: Daily food budget
            location_coords: Optional coordinates in "longitude,latitude" format
            
        Returns:
            List of restaurant recommendations with real data
        """
        try:
            logger.info(f"Getting real restaurant data for {destination}")
            
            # Step 1: Get destination coordinates if not provided
            if not location_coords:
                location_coords = self._get_destination_coordinates(destination)
            
            # Step 2: Search for restaurants using multiple strategies
            restaurants = []
            
            if self.use_mcp_tool and location_coords:
                # Strategy 1: Location-based search around destination
                location_restaurants = self._search_restaurants_by_location(
                    location_coords, destination
                )
                restaurants.extend(location_restaurants)
                
                # Strategy 2: Category-based searches
                category_restaurants = self._search_restaurants_by_categories(
                    destination, location_coords
                )
                restaurants.extend(category_restaurants)
                
                # Strategy 3: Keyword-based searches
                keyword_restaurants = self._search_restaurants_by_keywords(
                    destination
                )
                restaurants.extend(keyword_restaurants)
            
            # Step 3: Remove duplicates and get detailed information
            unique_restaurants = self._deduplicate_restaurants(restaurants)
            detailed_restaurants = self._get_detailed_restaurant_info(unique_restaurants)
            
            # Step 4: Enhance with AI-generated content
            enhanced_restaurants = self._enhance_restaurant_data(
                detailed_restaurants, destination, budget
            )
            
            # Step 5: Filter and rank restaurants
            final_restaurants = self._filter_and_rank_restaurants(
                enhanced_restaurants, budget
            )
            
            logger.info(f"Successfully retrieved {len(final_restaurants)} real restaurants")
            return final_restaurants[:15]  # Return top 15 restaurants
            
        except Exception as e:
            logger.error(f"Error getting real restaurant {str(e)}")
            # Fallback to AI-generated restaurants
            return self._get_fallback_restaurants(destination, budget)
    
    def _get_destination_coordinates(self, destination: str) -> Optional[str]:
        """Get coordinates for the destination using Amap geocoding."""
        try:
            if not self.use_mcp_tool:
                return None
                
            logger.info(f"Getting coordinates for {destination}")
            
            # Use Amap geocoding to get coordinates
            result = self.use_mcp_tool(
                'amap-maps',
                'maps_geo',
                {'address': destination}
            )
            
            if result and isinstance(result, dict):
                geocodes = result.get('geocodes', [])
                if geocodes and len(geocodes) > 0:
                    location = geocodes[0].get('location', '')
                    if location:
                        logger.info(f"Found coordinates for {destination}: {location}")
                        return location
            
            logger.warning(f"Could not get coordinates for {destination}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting coordinates for {destination}: {str(e)}")
            return None
    
    def _search_restaurants_by_location(
        self, 
        location_coords: str, 
        destination: str
    ) -> List[Dict[str, Any]]:
        """Search for restaurants around a specific location."""
        try:
            if not self.use_mcp_tool:
                return []
                
            logger.info(f"Searching restaurants around {location_coords}")
            
            restaurants = []
            
            # Search with different radii and keywords
            search_configs = [
                {'keywords': '餐厅', 'radius': '1000'},
                {'keywords': '美食', 'radius': '1500'},
                {'keywords': '小吃', 'radius': '800'},
                {'keywords': '火锅', 'radius': '2000'},
            ]
            
            for config in search_configs:
                try:
                    result = self.use_mcp_tool(
                        'amap-maps',
                        'maps_around_search',
                        {
                            'location': location_coords,
                            'keywords': config['keywords'],
                            'radius': config['radius']
                        }
                    )
                    
                    if result and isinstance(result, dict):
                        pois = result.get('pois', [])
                        for poi in pois[:10]:  # Limit to 10 per search
                            restaurant = self._parse_amap_poi(poi, 'location_search')
                            if restaurant:
                                restaurants.append(restaurant)
                                
                except Exception as e:
                    logger.warning(f"Error in location search with {config}: {str(e)}")
                    continue
            
            logger.info(f"Found {len(restaurants)} restaurants by location")
            return restaurants
            
        except Exception as e:
            logger.error(f"Error searching restaurants by location: {str(e)}")
            return []
    
    def _search_restaurants_by_categories(
        self, 
        destination: str, 
        location_coords: str
    ) -> List[Dict[str, Any]]:
        """Search for restaurants by different categories."""
        try:
            if not self.use_mcp_tool:
                return []
                
            restaurants = []
            
            # Search by different cuisine categories
            for category in self.restaurant_categories[:8]:  # Limit categories
                try:
                    # Text search for category in destination
                    result = self.use_mcp_tool(
                        'amap-maps',
                        'maps_text_search',
                        {
                            'keywords': f'{destination} {category}',
                            'city': destination
                        }
                    )
                    
                    if result and isinstance(result, dict):
                        pois = result.get('pois', [])
                        for poi in pois[:5]:  # Limit to 5 per category
                            restaurant = self._parse_amap_poi(poi, 'category_search')
                            if restaurant:
                                restaurant['cuisine_category'] = category
                                restaurants.append(restaurant)
                                
                except Exception as e:
                    logger.warning(f"Error searching category {category}: {str(e)}")
                    continue
            
            logger.info(f"Found {len(restaurants)} restaurants by categories")
            return restaurants
            
        except Exception as e:
            logger.error(f"Error searching restaurants by categories: {str(e)}")
            return []
    
    def _search_restaurants_by_keywords(self, destination: str) -> List[Dict[str, Any]]:
        """Search for restaurants using specific keywords."""
        try:
            if not self.use_mcp_tool:
                return []
                
            restaurants = []
            
            # Search with specific keywords
            keywords = [
                f'{destination} 推荐餐厅',
                f'{destination} 特色美食',
                f'{destination} 网红餐厅',
                f'{destination} 老字号',
                f'{destination} 当地菜'
            ]
            
            for keyword in keywords:
                try:
                    result = self.use_mcp_tool(
                        'amap-maps',
                        'maps_text_search',
                        {
                            'keywords': keyword,
                            'city': destination
                        }
                    )
                    
                    if result and isinstance(result, dict):
                        pois = result.get('pois', [])
                        for poi in pois[:3]:  # Limit to 3 per keyword
                            restaurant = self._parse_amap_poi(poi, 'keyword_search')
                            if restaurant:
                                restaurants.append(restaurant)
                                
                except Exception as e:
                    logger.warning(f"Error searching keyword {keyword}: {str(e)}")
                    continue
            
            logger.info(f"Found {len(restaurants)} restaurants by keywords")
            return restaurants
            
        except Exception as e:
            logger.error(f"Error searching restaurants by keywords: {str(e)}")
            return []
    
    def _parse_amap_poi(self, poi: Dict[str, Any], search_type: str) -> Optional[Dict[str, Any]]:
        """Parse Amap POI data into restaurant format."""
        try:
            if not poi or not isinstance(poi, dict):
                return None
            
            # Extract basic information
            name = poi.get('name', '').strip()
            if not name or len(name) < 2:
                return None
            
            # Skip non-restaurant POIs
            type_code = poi.get('type', '').lower()
            category = poi.get('typecode', '').lower()
            
            # Filter out non-restaurant POIs
            non_restaurant_keywords = [
                '银行', '医院', '学校', '酒店', '宾馆', '商场', 
                '超市', '加油站', '停车场', '地铁', '公交'
            ]
            
            if any(keyword in name for keyword in non_restaurant_keywords):
                return None
            
            restaurant = {
                'name': name,
                'amap_id': poi.get('id', ''),
                'address': poi.get('address', ''),
                'location': poi.get('location', ''),
                'type': poi.get('type', ''),
                'typecode': poi.get('typecode', ''),
                'business_area': poi.get('business_area', ''),
                'cityname': poi.get('cityname', ''),
                'adname': poi.get('adname', ''),
                'tel': poi.get('tel', ''),
                'distance': poi.get('distance', ''),
                'search_type': search_type,
                'data_source': 'amap',
                'retrieved_at': datetime.now().isoformat()
            }
            
            return restaurant
            
        except Exception as e:
            logger.warning(f"Error parsing Amap POI: {str(e)}")
            return None
    
    def _deduplicate_restaurants(self, restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate restaurants based on name and location."""
        try:
            seen = set()
            unique_restaurants = []
            
            for restaurant in restaurants:
                # Create a unique key based on name and location
                name = restaurant.get('name', '').strip().lower()
                location = restaurant.get('location', '').strip()
                amap_id = restaurant.get('amap_id', '').strip()
                
                # Use amap_id if available, otherwise use name + location
                if amap_id:
                    key = f"id:{amap_id}"
                else:
                    key = f"name:{name}:loc:{location}"
                
                if key not in seen:
                    seen.add(key)
                    unique_restaurants.append(restaurant)
            
            logger.info(f"Deduplicated {len(restaurants)} -> {len(unique_restaurants)} restaurants")
            return unique_restaurants
            
        except Exception as e:
            logger.error(f"Error deduplicating restaurants: {str(e)}")
            return restaurants
    
    def _get_detailed_restaurant_info(self, restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get detailed information for restaurants using Amap detail API."""
        try:
            if not self.use_mcp_tool:
                return restaurants
                
            detailed_restaurants = []
            
            for restaurant in restaurants:
                try:
                    amap_id = restaurant.get('amap_id', '')
                    if amap_id:
                        # Get detailed information from Amap
                        result = self.use_mcp_tool(
                            'amap-maps',
                            'maps_search_detail',
                            {'id': amap_id}
                        )
                        
                        if result and isinstance(result, dict):
                            pois = result.get('pois', [])
                            if pois and len(pois) > 0:
                                detailed_poi = pois[0]
                                # Merge detailed information
                                restaurant.update({
                                    'detailed_address': detailed_poi.get('address', restaurant.get('address', '')),
                                    'business_hours': detailed_poi.get('business_time', ''),
                                    'rating': detailed_poi.get('rating', ''),
                                    'cost': detailed_poi.get('cost', ''),
                                    'recommend': detailed_poi.get('recommend', ''),
                                    'atmosphere': detailed_poi.get('atmosphere', ''),
                                    'facility': detailed_poi.get('facility', ''),
                                    'hygiene': detailed_poi.get('hygiene', ''),
                                    'technology': detailed_poi.get('technology', ''),
                                    'service': detailed_poi.get('service', ''),
                                    'taste': detailed_poi.get('taste', ''),
                                    'environment': detailed_poi.get('environment', ''),
                                    'photos': detailed_poi.get('photos', []),
                                    'has_detailed_info': True
                                })
                    
                    detailed_restaurants.append(restaurant)
                    
                except Exception as e:
                    logger.warning(f"Error getting details for {restaurant.get('name', 'Unknown')}: {str(e)}")
                    # Add restaurant without detailed info
                    restaurant['has_detailed_info'] = False
                    detailed_restaurants.append(restaurant)
            
            logger.info(f"Retrieved detailed info for {len(detailed_restaurants)} restaurants")
            return detailed_restaurants
            
        except Exception as e:
            logger.error(f"Error getting detailed restaurant info: {str(e)}")
            return restaurants
    
    def _enhance_restaurant_data(
        self, 
        restaurants: List[Dict[str, Any]], 
        destination: str, 
        budget: float
    ) -> List[Dict[str, Any]]:
        """Enhance restaurant data with AI-generated content."""
        try:
            enhanced_restaurants = []
            daily_food_budget = budget * 0.20 / 7  # 20% of budget for 7 days
            
            for restaurant in restaurants:
                try:
                    # Generate AI enhancement for the restaurant
                    enhancement = self._generate_ai_enhancement(restaurant, destination, daily_food_budget)
                    
                    # Merge AI enhancement with real data
                    enhanced_restaurant = restaurant.copy()
                    enhanced_restaurant.update(enhancement)
                    
                    # Add budget analysis
                    enhanced_restaurant.update({
                        'budget_friendly': enhancement.get('estimated_cost', daily_food_budget) <= daily_food_budget,
                        'daily_food_budget': daily_food_budget,
                        'cost_ratio': enhancement.get('estimated_cost', daily_food_budget) / daily_food_budget if daily_food_budget > 0 else 1.0
                    })
                    
                    enhanced_restaurants.append(enhanced_restaurant)
                    
                except Exception as e:
                    logger.warning(f"Error enhancing restaurant {restaurant.get('name', 'Unknown')}: {str(e)}")
                    # Add restaurant without enhancement
                    enhanced_restaurants.append(restaurant)
            
            logger.info(f"Enhanced {len(enhanced_restaurants)} restaurants with AI content")
            return enhanced_restaurants
            
        except Exception as e:
            logger.error(f"Error enhancing restaurant {str(e)}")
            return restaurants
    
    def _generate_ai_enhancement(
        self, 
        restaurant: Dict[str, Any], 
        destination: str, 
        daily_budget: float
    ) -> Dict[str, Any]:
        """Generate AI enhancement for a restaurant."""
        try:
            name = restaurant.get('name', '')
            address = restaurant.get('address', '')
            business_area = restaurant.get('business_area', '')
            cuisine_category = restaurant.get('cuisine_category', '')
            
            prompt = f"""
            为{destination}的餐厅"{name}"生成详细信息。
            地址: {address}
            商圈: {business_area}
            类型: {cuisine_category}
            每日餐饮预算: {daily_budget:.0f}元
            
            请提供以下信息（用中文）：
            1. 简短描述（1-2句话）
            2. 推荐菜品（3-5个）
            3. 人均消费估算（数字）
            4. 餐厅特色
            5. 适合人群
            6. 用餐建议
            7. 评分（1-5分）
            
            请用简洁的格式回答，确保信息实用。
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse AI response
            enhancement = self._parse_ai_enhancement(response.text, daily_budget)
            
            return enhancement
            
        except Exception as e:
            logger.warning(f"Error generating AI enhancement: {str(e)}")
            return self._get_default_enhancement(daily_budget)
    
    def _parse_ai_enhancement(self, ai_response: str, daily_budget: float) -> Dict[str, Any]:
        """Parse AI enhancement response."""
        try:
            # Extract information using regex patterns
            enhancement = {}
            
            # Extract description
            desc_patterns = [
                r'描述[：:]\s*([^\n]+)',
                r'简介[：:]\s*([^\n]+)',
                r'^([^：:\n]{20,100})'
            ]
            
            for pattern in desc_patterns:
                match = re.search(pattern, ai_response, re.MULTILINE)
                if match:
                    enhancement['description'] = match.group(1).strip()
                    break
            
            # Extract specialties
            specialty_patterns = [
                r'推荐菜品[：:]\s*([^\n]+)',
                r'特色菜[：:]\s*([^\n]+)',
                r'招牌菜[：:]\s*([^\n]+)'
            ]
            
            specialties = []
            for pattern in specialty_patterns:
                match = re.search(pattern, ai_response, re.MULTILINE)
                if match:
                    items = re.split(r'[，,、]', match.group(1))
                    specialties = [item.strip() for item in items if item.strip()]
                    break
            
            enhancement['specialties'] = specialties[:5] if specialties else ['当地特色菜']
            
            # Extract cost
            cost_match = re.search(r'人均[^0-9]*(\d+)', ai_response)
            if cost_match:
                enhancement['estimated_cost'] = float(cost_match.group(1))
            else:
                enhancement['estimated_cost'] = daily_budget * 0.8
            
            # Extract rating
            rating_match = re.search(r'评分[：:]?\s*(\d+(?:\.\d+)?)', ai_response)
            if rating_match:
                enhancement['ai_rating'] = float(rating_match.group(1))
            else:
                enhancement['ai_rating'] = 4.0
            
            # Extract features
            feature_patterns = [
                r'特色[：:]\s*([^\n]+)',
                r'餐厅特色[：:]\s*([^\n]+)'
            ]
            
            for pattern in feature_patterns:
                match = re.search(pattern, ai_response, re.MULTILINE)
                if match:
                    enhancement['features'] = match.group(1).strip()
                    break
            
            # Set defaults for missing fields
            if 'description' not in enhancement:
                enhancement['description'] = '当地知名餐厅，提供优质的用餐体验。'
            
            if 'features' not in enhancement:
                enhancement['features'] = '环境舒适，服务周到'
            
            enhancement.update({
                'suitable_for': '朋友聚餐，家庭用餐',
                'dining_tips': '建议提前预订，高峰期可能需要等位',
                'price_range': self._categorize_price_range(enhancement.get('estimated_cost', daily_budget), daily_budget)
            })
            
            return enhancement
            
        except Exception as e:
            logger.warning(f"Error parsing AI enhancement: {str(e)}")
            return self._get_default_enhancement(daily_budget)
    
    def _categorize_price_range(self, cost: float, daily_budget: float) -> str:
        """Categorize price range based on cost and budget."""
        if cost <= daily_budget * 0.5:
            return '经济实惠'
        elif cost <= daily_budget * 1.2:
            return '中等消费'
        else:
            return '高端消费'
    
    def _get_default_enhancement(self, daily_budget: float) -> Dict[str, Any]:
        """Get default enhancement when AI fails."""
        return {
            'description': '当地餐厅，提供地道的美食体验。',
            'specialties': ['当地特色菜', '招牌菜'],
            'estimated_cost': daily_budget * 0.8,
            'ai_rating': 4.0,
            'features': '环境舒适，味道不错',
            'suitable_for': '各类人群',
            'dining_tips': '建议提前了解营业时间',
            'price_range': '中等消费'
        }
    
    def _filter_and_rank_restaurants(
        self, 
        restaurants: List[Dict[str, Any]], 
        budget: float
    ) -> List[Dict[str, Any]]:
        """Filter and rank restaurants based on quality and relevance."""
        try:
            # Filter out restaurants with insufficient data
            filtered_restaurants = []
            
            for restaurant in restaurants:
                # Basic quality checks
                name = restaurant.get('name', '').strip()
                if len(name) < 2:
                    continue
                
                # Skip if name contains obvious non-restaurant indicators
                skip_keywords = ['银行', '医院', '学校', '酒店', '宾馆', '商场', '超市']
                if any(keyword in name for keyword in skip_keywords):
                    continue
                
                filtered_restaurants.append(restaurant)
            
            # Rank restaurants by multiple factors
            def rank_restaurant(restaurant):
                score = 0
                
                # Factor 1: Data completeness (0-30 points)
                if restaurant.get('has_detailed_info'):
                    score += 15
                if restaurant.get('address'):
                    score += 5
                if restaurant.get('tel'):
                    score += 5
                if restaurant.get('business_hours'):
                    score += 5
                
                # Factor 2: AI rating (0-25 points)
                ai_rating = restaurant.get('ai_rating', 4.0)
                score += (ai_rating / 5.0) * 25
                
                # Factor 3: Budget compatibility (0-20 points)
                if restaurant.get('budget_friendly'):
                    score += 20
                elif restaurant.get('cost_ratio', 1.0) <= 1.5:
                    score += 10
                
                # Factor 4: Data source quality (0-15 points)
                if restaurant.get('data_source') == 'amap':
                    score += 15
                
                # Factor 5: Search relevance (0-10 points)
                search_type = restaurant.get('search_type', '')
                if search_type == 'location_search':
                    score += 10
                elif search_type == 'category_search':
                    score += 8
                elif search_type == 'keyword_search':
                    score += 6
                
                return score
            
            # Sort by ranking score
            filtered_restaurants.sort(key=rank_restaurant, reverse=True)
            
            logger.info(f"Filtered and ranked {len(filtered_restaurants)} restaurants")
            return filtered_restaurants
            
        except Exception as e:
            logger.error(f"Error filtering and ranking restaurants: {str(e)}")
            return restaurants
    
    def _get_fallback_restaurants(self, destination: str, budget: float) -> List[Dict[str, Any]]:
        """Get fallback restaurants when Amap integration fails."""
        try:
            daily_food_budget = budget * 0.20 / 7
            
            fallback_restaurants = [
                {
                    'name': f'{destination}老字号餐厅',
                    'description': f'{destination}历史悠久的传统餐厅，以地道的本地菜闻名。',
                    'address': f'{destination}市中心',
                    'specialties': ['传统地方菜', '招牌菜', '特色小食'],
                    'estimated_cost': daily_food_budget * 0.8,
                    'ai_rating': 4.3,
                    'price_range': '中等消费',
                    'features': '历史悠久，口味地道',
                    'suitable_for': '家庭聚餐，朋友聚会',
                    'dining_tips': '建议提前预订，尝试招牌菜',
                    'data_source': 'ai_fallback',
                    'budget_friendly': True
                },
                {
                    'name': f'{destination}特色小吃街',
                    'description': f'{destination}著名的小吃聚集地，汇集了各种当地特色小吃。',
                    'address': f'{destination}小吃街',
                    'specialties': ['当地小吃', '街头美食', '特色点心'],
                    'estimated_cost': daily_food_budget * 0.4,
                    'ai_rating': 4.1,
                    'price_range': '经济实惠',
                    'features': '品种丰富，价格实惠',
                    'suitable_for': '年轻人，美食爱好者',
                    'dining_tips': '晚上更热闹，注意卫生',
                    'data_source': 'ai_fallback',
                    'budget_friendly': True
                },
                {
                    'name': f'{destination}精品餐厅',
                    'description': f'{destination}高端餐厅，提供精致的料理和优雅的用餐环境。',
                    'address': f'{destination}商业区',
                    'specialties': ['精致料理', '创意菜品', '特色套餐'],
                    'estimated_cost': daily_food_budget * 1.5,
                    'ai_rating': 4.6,
                    'price_range': '高端消费',
                    'features': '环境优雅，服务精致',
                    'suitable_for': '商务宴请，特殊场合',
                    'dining_tips': '需要提前预订，着装要求较高',
                    'data_source': 'ai_fallback',
                    'budget_friendly': False
                }
            ]
            
            logger.info(f"Generated {len(fallback_restaurants)} fallback restaurants")
            return fallback_restaurants
            
        except Exception as e:
            logger.error(f"Error generating fallback restaurants: {str(e)}")
            return []
