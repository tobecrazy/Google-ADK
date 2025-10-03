"""
Restaurant Service
Provides comprehensive restaurant recommendations using multiple data sources
"""

import os
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re

# Add the parent directory to sys.path to enable absolute imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from travel_agent.utils.restaurant_aggregator import RestaurantDataAggregator

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

logger = logging.getLogger(__name__)

class RestaurantService:
    """Enhanced service for comprehensive restaurant data from multiple sources."""
    
    def __init__(self, use_mcp_tool=None):
        """Initialize the restaurant service with enhanced capabilities."""
        # NOTE: Google ADK automatically provides MCP tools to the LLM agent
        # The LLM agent can call MCP tools directly without a wrapper function
        
        # Store the MCP tool caller if provided
        self.use_mcp_tool = use_mcp_tool
        
        # Initialize the restaurant data aggregator
        self.restaurant_aggregator = RestaurantDataAggregator()
        
        # Initialize ModelScope LLM for data enhancement
        self.model = self._create_llm_model()
        
        # Restaurant categories for search
        self.restaurant_categories = [
            '餐厅', '中餐厅', '西餐厅', '火锅店', '烧烤店', 
            '小吃店', '咖啡厅', '茶餐厅', '日料', '韩料',
            '川菜', '粤菜', '湘菜', '东北菜', '海鲜'
        ]
        
        logger.info("Enhanced Restaurant Service initialized (Google ADK handles MCP integration automatically)")
    
    def _create_llm_model(self):
        """Creates a LiteLLM model with fallback options for rate limits."""
        import time
        from google.adk.models.lite_llm import LiteLlm
        
        # List of models to try in order (most reliable and least rate-limited first)
        models_to_try = [
            "Qwen/Qwen3-235B-A22B",
            "deepseek-ai/DeepSeek-V3.1", 
            "deepseek-ai/DeepSeek-R1-0528"
        ]
        
        # For ModelScope, we can use a dummy API key or the actual ModelScope token if available
        api_key = os.getenv("MODELSCOPE_API_KEY") or "dummy_key"
        if not os.getenv("MODELSCOPE_API_KEY"):
            logger.warning("MODELSCOPE_API_KEY not found, using dummy key for ModelScope")
        
        for i, model in enumerate(models_to_try):
            try:
                logger.info(f"Attempting to create model with: {model} (attempt {i+1}/{len(models_to_try)})")
                
                # Configure model-specific parameters
                model_kwargs = {
                    "model": model,
                    "api_key": api_key,
                    "api_base": "https://api-inference.modelscope.cn/v1",
                    "custom_llm_provider": "openai",
                    "max_retries": 2,  # Reduced retries to fail faster
                    "timeout": 30
                }
                
                # Fix for Qwen models: set enable_thinking=false for non-streaming calls
                if "Qwen" in model:
                    logger.info(f"🔧 Configuring Qwen model {model} with enable_thinking=false")
                    model_kwargs["enable_thinking"] = False
                
                llm_model = LiteLlm(**model_kwargs)
                logger.info(f"✅ Successfully created model with: {model}")
                return llm_model
            except Exception as e:
                logger.error(f"❌ Failed to create model with {model}: {str(e)[:100]}...")
                if model != models_to_try[-1]:  # Not the last model
                    logger.info(f"⏭️  Trying next model in {2}s...")
                    time.sleep(2)  # Brief delay before trying next model
                continue
        
        # If all models fail, return None and log warning
        logger.warning("❌ All model options failed. AI enhancement will be limited.")
        return None
    
    def get_restaurants(
        self,
        destination: str,
        budget: float,
        location_coords: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get comprehensive restaurant recommendations from multiple sources.
        
        Args:
            destination: Target destination
            budget: Total travel budget (daily food budget will be calculated)
            location_coords: Optional coordinates in "longitude,latitude" format
            
        Returns:
            List of comprehensive restaurant recommendations
        """
        try:
            logger.info(f"Getting comprehensive restaurant data for {destination}")
            
            # Use the restaurant aggregator to get comprehensive data
            restaurants = self.restaurant_aggregator.get_comprehensive_restaurant_data(
                destination=destination,
                budget=budget,
                location_coords=location_coords,
                max_results=20
            )
            
            # Additional post-processing if needed
            processed_restaurants = self._post_process_restaurants(restaurants, destination, budget)
            
            logger.info(f"Successfully retrieved {len(processed_restaurants)} comprehensive restaurants")
            return processed_restaurants[:15]  # Return top 15 restaurants
            
        except Exception as e:
            logger.error(f"Error getting comprehensive restaurant data: {str(e)}")
            # Fallback to emergency restaurants
            return self._get_emergency_fallback_restaurants(destination, budget)
    
    def _post_process_restaurants(
        self,
        restaurants: List[Dict[str, Any]],
        destination: str,
        budget: float
    ) -> List[Dict[str, Any]]:
        """Post-process restaurants with additional enhancements."""
        try:
            daily_food_budget = budget * 0.20 / 7
            
            for restaurant in restaurants:
                # Add service-specific metadata
                restaurant['service_processed'] = True
                restaurant['processed_at'] = datetime.now().isoformat()
                
                # Ensure Chinese descriptions for better user experience
                if not restaurant.get('description') or len(restaurant.get('description', '')) < 10:
                    restaurant['description'] = self._generate_chinese_description(
                        restaurant, destination
                    )
                
                # Add dining recommendations
                restaurant['dining_recommendations'] = self._generate_dining_recommendations(
                    restaurant, daily_food_budget
                )
                
                # Add accessibility info
                restaurant['accessibility'] = self._assess_accessibility(restaurant)
            
            return restaurants
            
        except Exception as e:
            logger.error(f"Error post-processing restaurants: {str(e)}")
            return restaurants
    
    def _generate_chinese_description(self, restaurant: Dict[str, Any], destination: str) -> str:
        """Generate a Chinese description for the restaurant."""
        try:
            name = restaurant.get('name', '餐厅')
            cuisine = restaurant.get('cuisine', 'Local')
            price_range = restaurant.get('price_range', 'Mid-range')
            
            # Map English terms to Chinese
            cuisine_map = {
                'Local': '当地菜',
                'Local Traditional': '传统菜',
                'Street Food': '街头小食',
                'Fine Dining': '精致料理',
                'International': '国际料理',
                'Chinese': '中餐',
                'Cafe': '咖啡厅'
            }
            
            price_map = {
                'Budget': '经济实惠',
                'Mid-range': '中等价位',
                'High-end': '高端消费',
                'Luxury': '奢华体验'
            }
            
            chinese_cuisine = cuisine_map.get(cuisine, cuisine)
            chinese_price = price_map.get(price_range, price_range)
            
            return f"{name}是{destination}的一家{chinese_cuisine}餐厅，{chinese_price}，提供优质的用餐体验和地道的美食。"
            
        except Exception as e:
            logger.warning(f"Error generating Chinese description: {str(e)}")
            return f"{destination}当地餐厅，提供美味的料理和舒适的用餐环境。"
    
    def _generate_dining_recommendations(self, restaurant: Dict[str, Any], daily_budget: float) -> List[str]:
        """Generate dining recommendations for the restaurant."""
        try:
            recommendations = []
            
            # Budget-based recommendations
            cost = restaurant.get('estimated_cost', daily_budget)
            if cost <= daily_budget * 0.7:
                recommendations.append("性价比很高，适合日常用餐")
            elif cost <= daily_budget * 1.2:
                recommendations.append("价格合理，值得一试")
            else:
                recommendations.append("价格较高，适合特殊场合")
            
            # Cuisine-based recommendations
            cuisine = restaurant.get('cuisine', '')
            if 'Local' in cuisine or '当地' in cuisine:
                recommendations.append("体验当地特色，不容错过")
            elif 'Street' in cuisine or '小吃' in cuisine:
                recommendations.append("街头美食，感受当地文化")
            elif 'Fine' in cuisine or '精致' in cuisine:
                recommendations.append("精致用餐，适合商务或约会")
            
            # Rating-based recommendations
            rating = restaurant.get('rating', 0)
            if rating >= 4.5:
                recommendations.append("评分很高，强烈推荐")
            elif rating >= 4.0:
                recommendations.append("口碑不错，值得推荐")
            
            # Source-based recommendations
            source = restaurant.get('source', '')
            if source == 'amap':
                recommendations.append("真实数据，信息可靠")
            elif source == 'tripadvisor':
                recommendations.append("国际游客推荐")
            elif source == 'food_blog':
                recommendations.append("美食博主推荐")
            
            return recommendations[:3]  # Return top 3 recommendations
            
        except Exception as e:
            logger.warning(f"Error generating dining recommendations: {str(e)}")
            return ["推荐尝试当地特色菜"]
    
    def _assess_accessibility(self, restaurant: Dict[str, Any]) -> Dict[str, str]:
        """Assess restaurant accessibility information."""
        try:
            accessibility = {
                'location_accessibility': '位置便利',
                'price_accessibility': '价格适中',
                'service_accessibility': '服务友好'
            }
            
            # Assess based on available data
            if restaurant.get('address'):
                if any(keyword in restaurant['address'] for keyword in ['市中心', '商业区', '步行街']):
                    accessibility['location_accessibility'] = '位置优越，交通便利'
                elif any(keyword in restaurant['address'] for keyword in ['郊区', '远离']):
                    accessibility['location_accessibility'] = '位置较远，建议打车'
            
            price_range = restaurant.get('price_range', '')
            if price_range in ['Budget', '经济实惠']:
                accessibility['price_accessibility'] = '价格亲民，学生友好'
            elif price_range in ['High-end', '高端消费']:
                accessibility['price_accessibility'] = '价格较高，适合特殊场合'
            
            if restaurant.get('tel'):
                accessibility['service_accessibility'] = '可电话预订，服务便民'
            
            return accessibility
            
        except Exception as e:
            logger.warning(f"Error assessing accessibility: {str(e)}")
            return {'general': '一般可达性'}
    
    def _get_emergency_fallback_restaurants(self, destination: str, budget: float) -> List[Dict[str, Any]]:
        """Get emergency fallback restaurants when all systems fail."""
        try:
            daily_food_budget = budget * 0.20 / 7
            
            emergency_restaurants = [
                {
                    'name': f'{destination}当地餐厅',
                    'description': f'{destination}传统餐厅，提供地道的当地菜肴和温馨的用餐环境。',
                    'cuisine': 'Local Traditional',
                    'price_range': 'Mid-range',
                    'estimated_cost': daily_food_budget * 0.8,
                    'rating': 4.2,
                    'specialties': ['当地特色菜', '传统料理'],
                    'location': destination,
                    'source': 'emergency_fallback',
                    'data_source': 'service_emergency',
                    'final_score': 60.0,
                    'budget_friendly': True,
                    'dining_recommendations': ['体验当地特色', '价格合理'],
                    'accessibility': {'general': '位置便利，价格适中'}
                },
                {
                    'name': f'{destination}小食街',
                    'description': f'{destination}著名小食聚集地，各种当地小吃和街头美食的天堂。',
                    'cuisine': 'Street Food',
                    'price_range': 'Budget',
                    'estimated_cost': daily_food_budget * 0.4,
                    'rating': 4.0,
                    'specialties': ['街头小吃', '当地小食'],
                    'location': destination,
                    'source': 'emergency_fallback',
                    'data_source': 'service_emergency',
                    'final_score': 55.0,
                    'budget_friendly': True,
                    'dining_recommendations': ['性价比很高', '感受当地文化'],
                    'accessibility': {'general': '价格亲民，位置热闹'}
                }
            ]
            
            logger.warning(f"Using emergency fallback: generated {len(emergency_restaurants)} restaurants")
            return emergency_restaurants
            
        except Exception as e:
            logger.error(f"Error generating emergency fallback restaurants: {str(e)}")
            return []
    
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
