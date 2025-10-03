"""
Attraction Service
Provides attraction and points of interest data
"""

import os
import re
import logging
from typing import Dict, Any, List
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.image_handler import ImageHandler

logger = logging.getLogger(__name__)

class AttractionService:
    """Service for attraction and POI data."""
    
    def __init__(self, mcp_tool_caller=None):
        """Initialize the attraction service."""
        # Initialize ModelScope LLM for attraction data generation using shared factory
        from travel_agent.utils.model_factory import create_llm_model
        self.model = create_llm_model("AttractionService")
        
        # Initialize image handler for attraction images
        self.image_handler = ImageHandler()
        
        # Store MCP tool caller for real-time data
        self.mcp_tool_caller = mcp_tool_caller
        
        logger.info("Attraction Service initialized with MCP integration")
    
    def get_attractions(self, destination: str, budget: float) -> List[Dict[str, Any]]:
        """
        Get attractions and points of interest for a destination.
        
        Now enhanced with real-time amap MCP data integration for accurate attraction information.
        
        Args:
            destination: Target destination
            budget: Total budget for activities
            
        Returns:
            List of attraction data
        """
        try:
            logger.info(f"Getting attractions for {destination}")
            
            # Try to get real attractions from amap MCP first
            real_attractions = []
            if self.mcp_tool_caller:
                try:
                    real_attractions = self._get_real_attractions_from_amap(destination, budget)
                    logger.info(f"Successfully retrieved {len(real_attractions)} real attractions from amap")
                except Exception as e:
                    logger.warning(f"Failed to get real attractions from amap: {str(e)}")
            
            # If we have real attractions, use them; otherwise fall back to AI-generated
            if real_attractions and len(real_attractions) >= 3:
                enhanced_attractions = real_attractions
                logger.info(f"Using {len(real_attractions)} real attractions from amap")
            else:
                logger.info("Falling back to AI-generated attractions")
                enhanced_attractions = self._generate_attractions_with_ai(destination, budget)
            
            # Enhance with additional details
            final_attractions = self._enhance_attraction_data(enhanced_attractions, budget)
            
            # Add images to attractions
            try:
                logger.info(f"Adding images to {len(final_attractions)} attractions for {destination}")
                attractions_with_images = self._add_images_to_attractions(destination, final_attractions)
                
                # Log image success rate
                with_images = sum(1 for attr in attractions_with_images if attr.get('has_image', False))
                logger.info(f"Successfully added images to {with_images}/{len(attractions_with_images)} attractions")
                
                return attractions_with_images
            except Exception as e:
                logger.warning(f"Failed to add images to attractions: {str(e)}")
                # Return attractions without images if image processing fails
                for attraction in final_attractions:
                    attraction['image_url'] = None
                    attraction['has_image'] = False
                return final_attractions
            
        except Exception as e:
            logger.error(f"Error getting attractions: {str(e)}")
            return self._get_fallback_attractions(destination, budget)
    
    def _add_images_to_attractions(self, destination: str, attractions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add images to attractions using multiple sources."""
        enhanced_attractions = []
        
        for attraction in attractions:
            try:
                attraction_name = attraction.get('name', '')
                
                # Generate search terms for better image matching
                search_terms = [
                    f"{destination} {attraction_name}",
                    f"{attraction_name} {destination}",
                    attraction_name,
                    f"{destination} 景点"
                ]
                
                # Try to get image from multiple sources
                # Try to get image from image handler
                image_url = None
                for search_term in search_terms:
                    try:
                        # Use the new image handler method
                        image_url = self.image_handler._get_unsplash_image(search_term)
                        if image_url:
                            break
                    except Exception as e:
                        logger.debug(f"Failed to get image for '{search_term}': {e}")
                        continue
                
                # If no image found, try fallback sources
                if not image_url:
                    try:
                        image_url = self.image_handler._try_picsum_image(f"{destination} landmark")
                    except Exception as e:
                        logger.debug(f"Picsum fallback failed: {e}")
                        # Generate a placeholder URL directly
                        image_url = self.image_handler._generate_placeholder_url(f"{destination} attraction")
                
                # Add image information to attraction
                enhanced_attraction = attraction.copy()
                enhanced_attraction['image_url'] = image_url
                enhanced_attraction['has_image'] = bool(image_url)
                
                enhanced_attractions.append(enhanced_attraction)
                
            except Exception as e:
                logger.error(f"Error adding image to attraction {attraction.get('name', 'Unknown')}: {e}")
                enhanced_attraction = attraction.copy()
                enhanced_attraction['image_url'] = None
                enhanced_attraction['has_image'] = False
                enhanced_attractions.append(enhanced_attraction)
        
        return enhanced_attractions
    
    def _get_real_attractions_from_amap(self, destination: str, budget: float) -> List[Dict[str, Any]]:
        """Get real attractions from amap MCP tools."""
        try:
            logger.info(f"Fetching real attractions for {destination} using amap MCP")
            
            real_attractions = []
            
            # Search for different types of attractions using amap
            attraction_categories = [
                "景点",
                "旅游景点", 
                "著名景点",
                "博物馆",
                "公园",
                "历史建筑",
                "文化景点"
            ]
            
            # Get city center coordinates first
            city_center = self._get_city_center_coordinates(destination)
            
            for category in attraction_categories:
                try:
                    # Search by text
                    text_results = self._search_attractions_by_category(destination, category)
                    if text_results:
                        real_attractions.extend(text_results)
                    
                    # Search around city center if we have coordinates
                    if city_center:
                        around_results = self._search_attractions_around_location(city_center, category)
                        if around_results:
                            real_attractions.extend(around_results)
                    
                    # Limit to avoid too many API calls
                    if len(real_attractions) >= 15:
                        break
                        
                except Exception as e:
                    logger.warning(f"Failed to search for {category} attractions: {str(e)}")
                    continue
            
            # Remove duplicates and get detailed information
            unique_attractions = self._remove_duplicate_attractions(real_attractions)
            detailed_attractions = self._get_detailed_attraction_info(unique_attractions[:10])  # Limit to top 10
            
            logger.info(f"Successfully retrieved {len(detailed_attractions)} real attractions from amap")
            return detailed_attractions
            
        except Exception as e:
            logger.error(f"Error getting real attractions from amap: {str(e)}")
            return []
    
    def _get_city_center_coordinates(self, destination: str) -> Dict[str, Any]:
        """Get city center coordinates using amap geocoding."""
        try:
            if not self.mcp_tool_caller:
                return None
                
            logger.info(f"Getting coordinates for {destination}")
            
            # Use amap geocoding to get city center
            result = self.mcp_tool_caller(
                'maps_geo',
                {'address': destination},
                server_name='Amap Maps Server'
            )
            
            if result and result.get('success') and result.get('result'):
                geocode_data = result['result']
                if isinstance(geocode_data, dict) and 'location' in geocode_data:
                    location = geocode_data['location']
                    logger.info(f"Found coordinates for {destination}: {location}")
                    return {
                        'longitude': location.split(',')[0],
                        'latitude': location.split(',')[1],
                        'location_string': location
                    }
            
            logger.warning(f"Could not get coordinates for {destination}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting city center coordinates: {str(e)}")
            return None
    
    def _search_attractions_by_category(self, destination: str, category: str) -> List[Dict[str, Any]]:
        """Search attractions by category using amap text search."""
        try:
            if not self.mcp_tool_caller:
                return []
                
            logger.info(f"Searching for {category} in {destination}")
            
            # Use amap text search
            result = self.mcp_tool_caller(
                'maps_text_search',
                {
                    'keywords': f'{destination} {category}',
                    'city': destination
                },
                server_name='Amap Maps Server'
            )
            
            if result and result.get('success') and result.get('result'):
                search_data = result['result']
                return self._parse_amap_search_results(search_data, 'text_search')
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching attractions by category {category}: {str(e)}")
            return []
    
    def _search_attractions_around_location(self, location: Dict[str, Any], category: str) -> List[Dict[str, Any]]:
        """Search attractions around a specific location using amap around search."""
        try:
            if not self.mcp_tool_caller or not location:
                return []
                
            logger.info(f"Searching for {category} around location {location.get('location_string', '')}")
            
            # Use amap around search
            result = self.mcp_tool_caller(
                'maps_around_search',
                {
                    'keywords': category,
                    'location': location['location_string'],
                    'radius': '5000'  # 5km radius
                },
                server_name='Amap Maps Server'
            )
            
            if result and result.get('success') and result.get('result'):
                search_data = result['result']
                return self._parse_amap_search_results(search_data, 'around_search')
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching attractions around location: {str(e)}")
            return []
    
    def _parse_amap_search_results(self, search_data: Any, search_type: str) -> List[Dict[str, Any]]:
        """Parse amap search results into attraction format."""
        try:
            attractions = []
            
            # Handle different response formats
            pois = []
            if isinstance(search_data, dict):
                if 'pois' in search_data:
                    pois = search_data['pois']
                elif 'results' in search_data:
                    pois = search_data['results']
                elif isinstance(search_data.get('data'), list):
                    pois = search_data['data']
            elif isinstance(search_data, list):
                pois = search_data
            
            logger.info(f"Parsing {len(pois)} POIs from {search_type}")
            
            for poi in pois[:10]:  # Limit to top 10 results per search
                try:
                    if not isinstance(poi, dict):
                        continue
                        
                    attraction = {
                        'name': poi.get('name', '未知景点'),
                        'description': self._generate_description_from_poi(poi),
                        'category': self._categorize_poi(poi),
                        'duration': self._estimate_duration_from_poi(poi),
                        'entrance_fee': self._estimate_fee_from_poi(poi),
                        'rating': self._extract_rating_from_poi(poi),
                        'address': poi.get('address', ''),
                        'location': poi.get('location', ''),
                        'phone': poi.get('tel', ''),
                        'source': 'amap_real_data',
                        'poi_id': poi.get('id', ''),
                        'search_type': search_type
                    }
                    
                    attractions.append(attraction)
                    
                except Exception as e:
                    logger.warning(f"Error parsing individual POI: {str(e)}")
                    continue
            
            logger.info(f"Successfully parsed {len(attractions)} attractions from {search_type}")
            return attractions
            
        except Exception as e:
            logger.error(f"Error parsing amap search results: {str(e)}")
            return []
    
    def _generate_description_from_poi(self, poi: Dict[str, Any]) -> str:
        """Generate description from POI data."""
        try:
            name = poi.get('name', '')
            address = poi.get('address', '')
            type_code = poi.get('type', '')
            
            # Use available information to create description based on attraction types
            if '博物馆' in name or 'museum' in name.lower():
                return f"{name}是一座重要的博物馆，展示丰富的文化和历史藏品，是了解当地文化的绝佳场所。"
            elif '公园' in name or 'park' in name.lower():
                return f"{name}是一个美丽的公园，提供休闲娱乐和自然风光，适合散步和放松。"
            elif '塔' in name or 'tower' in name.lower():
                return f"{name}是当地的标志性建筑，提供城市全景视野，是拍照和观光的热门地点。"
            elif '寺' in name or '庙' in name:
                return f"{name}是一座历史悠久的宗教建筑，具有深厚的文化底蕴和精美的建筑艺术。"
            elif '外滩' in name or '滨江' in name or '江滨' in name:
                return f"{name}是当地著名的滨水景观区，汇集了各种风格的历史建筑，是欣赏江景的最佳地点。"
            elif '园' in name and ('古' in name or '传统' in name or '历史' in name):
                return f"{name}是当地著名的古典园林，展现了中国传统园林艺术的精髓，是体验传统文化的理想场所。"
            elif '广场' in name or 'square' in name.lower():
                return f"{name}是当地的中心广场，是市民休闲和文化活动的重要场所，充满当地生活气息。"
            elif '街' in name or 'street' in name.lower():
                return f"{name}是当地的特色街区，保留了传统建筑风格，是体验当地文化和购物的好去处。"
            else:
                return f"{name}是当地的著名景点，位于{address}，值得一游。"
                
        except Exception as e:
            logger.warning(f"Error generating description from POI: {str(e)}")
            return "这是一个值得参观的景点。"
    
    def _categorize_poi(self, poi: Dict[str, Any]) -> str:
        """Categorize POI based on its properties."""
        try:
            name = poi.get('name', '').lower()
            poi_type = poi.get('type', '').lower()
            
            if any(keyword in name for keyword in ['博物馆', 'museum']):
                return '文化教育'
            elif any(keyword in name for keyword in ['公园', 'park', '花园', 'garden']):
                return '自然风光'
            elif any(keyword in name for keyword in ['塔', 'tower', '大厦', 'building']):
                return '观光地标'
            elif any(keyword in name for keyword in ['寺', '庙', 'temple']):
                return '宗教文化'
            elif any(keyword in name for keyword in ['滨江', '江滨', '外滩', '步行街', '老街', '古街']):
                return '历史文化'
            elif any(keyword in name for keyword in ['广场', 'square']):
                return '城市地标'
            elif any(keyword in name for keyword in ['山', 'mountain', '峰', 'peak']):
                return '自然风光'
            elif any(keyword in name for keyword in ['湖', 'lake', '河', 'river', '江', 'sea']):
                return '自然风光'
            else:
                return '综合景点'
                
        except Exception as e:
            logger.warning(f"Error categorizing POI: {str(e)}")
            return '综合景点'
    
    def _estimate_duration_from_poi(self, poi: Dict[str, Any]) -> str:
        """Estimate visit duration based on POI type."""
        try:
            name = poi.get('name', '').lower()
            
            if any(keyword in name for keyword in ['博物馆', 'museum']):
                return '2-3小时'
            elif any(keyword in name for keyword in ['公园', 'park']):
                return '1-2小时'
            elif any(keyword in name for keyword in ['塔', 'tower']):
                return '1小时'
            elif any(keyword in name for keyword in ['滨江', '江滨', '外滩', '步行街']):
                return '2-3小时'
            elif any(keyword in name for keyword in ['园', 'garden']) and any(keyword in name for keyword in ['古', '传统', '历史']):
                return '2-3小时'
            elif any(keyword in name for keyword in ['寺', '庙', 'temple']):
                return '1-2小时'
            elif any(keyword in name for keyword in ['广场', 'square']):
                return '1小时'
            elif any(keyword in name for keyword in ['山', 'mountain', '峰', 'peak']):
                return '3-4小时'
            elif any(keyword in name for keyword in ['湖', 'lake', '河', 'river']):
                return '1-2小时'
            else:
                return '1-2小时'
                
        except Exception as e:
            logger.warning(f"Error estimating duration: {str(e)}")
            return '1-2小时'
    
    def _estimate_fee_from_poi(self, poi: Dict[str, Any]) -> float:
        """Estimate entrance fee based on POI type."""
        try:
            name = poi.get('name', '').lower()
            
            if any(keyword in name for keyword in ['博物馆', 'museum']):
                return 20.0
            elif any(keyword in name for keyword in ['塔', 'tower']):
                return 50.0
            elif any(keyword in name for keyword in ['园', 'garden']) and any(keyword in name for keyword in ['古', '传统', '历史']):
                return 30.0
            elif any(keyword in name for keyword in ['公园', 'park', '滨江', '江滨', '外滩', '广场', 'square']):
                return 0.0
            elif any(keyword in name for keyword in ['寺', '庙', 'temple']):
                return 10.0
            elif any(keyword in name for keyword in ['山', 'mountain', '峰', 'peak']):
                return 15.0
            else:
                return 10.0
                
        except Exception as e:
            logger.warning(f"Error estimating fee: {str(e)}")
            return 0.0
    
    def _extract_rating_from_poi(self, poi: Dict[str, Any]) -> float:
        """Extract or estimate rating from POI data."""
        try:
            # Check if rating is available in POI data
            if 'rating' in poi:
                return float(poi['rating'])
            elif 'score' in poi:
                return float(poi['score'])
            else:
                # Estimate based on POI type - use generic categories instead of specific attractions
                name = poi.get('name', '').lower()
                if any(keyword in name for keyword in ['博物馆', 'museum']):
                    return 4.2
                elif any(keyword in name for keyword in ['塔', 'tower', '观景台']):
                    return 4.3
                elif any(keyword in name for keyword in ['滨江', '江滨', '外滩', '步行街']):
                    return 4.4
                elif any(keyword in name for keyword in ['园', 'garden']) and any(keyword in name for keyword in ['古', '传统', '历史']):
                    return 4.3
                elif any(keyword in name for keyword in ['寺', '庙', 'temple']):
                    return 4.1
                elif any(keyword in name for keyword in ['公园', 'park']):
                    return 4.0
                elif any(keyword in name for keyword in ['山', 'mountain', '峰', 'peak']):
                    return 4.2
                else:
                    return 4.0
                    
        except Exception as e:
            logger.warning(f"Error extracting rating: {str(e)}")
            return 4.0
    
    def _remove_duplicate_attractions(self, attractions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate attractions based on name similarity."""
        try:
            unique_attractions = []
            seen_names = set()
            
            for attraction in attractions:
                name = attraction.get('name', '').lower().strip()
                
                # Check for exact duplicates
                if name in seen_names:
                    continue
                
                # Check for similar names (simple similarity check)
                is_duplicate = False
                for seen_name in seen_names:
                    if self._names_are_similar(name, seen_name):
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    unique_attractions.append(attraction)
                    seen_names.add(name)
            
            logger.info(f"Removed duplicates: {len(attractions)} -> {len(unique_attractions)}")
            return unique_attractions
            
        except Exception as e:
            logger.error(f"Error removing duplicates: {str(e)}")
            return attractions
    
    def _names_are_similar(self, name1: str, name2: str) -> bool:
        """Check if two attraction names are similar (simple implementation)."""
        try:
            # Simple similarity check - can be enhanced with more sophisticated algorithms
            if len(name1) < 3 or len(name2) < 3:
                return name1 == name2
            
            # Check if one name contains the other
            if name1 in name2 or name2 in name1:
                return True
            
            # Check for common words
            words1 = set(name1.split())
            words2 = set(name2.split())
            common_words = words1.intersection(words2)
            
            # If they share significant words, consider them similar
            if len(common_words) >= min(len(words1), len(words2)) * 0.7:
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking name similarity: {str(e)}")
            return False
    
    def _get_detailed_attraction_info(self, attractions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get detailed information for attractions using amap detail search."""
        try:
            detailed_attractions = []
            
            for attraction in attractions:
                try:
                    poi_id = attraction.get('poi_id')
                    if poi_id and self.mcp_tool_caller:
                        # Try to get detailed information
                        detail_result = self.mcp_tool_caller(
                            'maps_search_detail',
                            {'id': poi_id},
                            server_name='Amap Maps Server'
                        )
                        
                        if detail_result and detail_result.get('success'):
                            # Enhance attraction with detailed info
                            detailed_info = detail_result.get('result', {})
                            attraction = self._merge_detailed_info(attraction, detailed_info)
                    
                    detailed_attractions.append(attraction)
                    
                except Exception as e:
                    logger.warning(f"Error getting details for attraction {attraction.get('name', 'Unknown')}: {str(e)}")
                    # Add attraction without detailed info
                    detailed_attractions.append(attraction)
            
            return detailed_attractions
            
        except Exception as e:
            logger.error(f"Error getting detailed attraction info: {str(e)}")
            return attractions
    
    def _merge_detailed_info(self, attraction: Dict[str, Any], detailed_info: Dict[str, Any]) -> Dict[str, Any]:
        """Merge detailed information into attraction data."""
        try:
            # Update with more detailed information if available
            if isinstance(detailed_info, dict):
                if 'business_hours' in detailed_info:
                    attraction['opening_hours'] = detailed_info['business_hours']
                if 'photos' in detailed_info and detailed_info['photos']:
                    attraction['photos'] = detailed_info['photos'][:3]  # Keep top 3 photos
                if 'rating' in detailed_info:
                    attraction['rating'] = float(detailed_info['rating'])
                if 'price' in detailed_info:
                    attraction['entrance_fee'] = self._parse_price_info(detailed_info['price'])
            
            return attraction
            
        except Exception as e:
            logger.warning(f"Error merging detailed info: {str(e)}")
            return attraction
    
    def _parse_price_info(self, price_info: Any) -> float:
        """Parse price information from detailed POI data."""
        try:
            if isinstance(price_info, (int, float)):
                return float(price_info)
            elif isinstance(price_info, str):
                # Extract numeric value from price string
                import re
                price_match = re.search(r'(\d+(?:\.\d+)?)', price_info)
                if price_match:
                    return float(price_match.group(1))
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Error parsing price info: {str(e)}")
            return 0.0
    
    def _generate_attractions_with_ai(self, destination: str, budget: float) -> List[Dict[str, Any]]:
        """Use AI to generate attraction recommendations."""
        try:
            activities_budget = budget * 0.15  # 15% of total budget for activities
            
            prompt = f"""
            请为{destination}生成详细的景点和活动清单，考虑总活动预算为{activities_budget:.2f}元。

            请为每个景点提供以下信息（全部使用中文）：
            1. 景点名称（使用中文名称）
            2. 简要描述（2-3句话，中文）
            3. 类别（历史文化、自然风光、娱乐休闲、宗教场所等）
            4. 预计游览时长
            5. 大概门票价格（如有）
            6. 最佳游览时间
            7. 难度等级（简单、中等、困难）
            8. 适合年龄
            9. 是否允许拍照（是/否/限制）
            10. 无障碍设施信息

            请包含以下类型的景点：
            - 必游著名景点（5-7个）
            - 隐藏宝藏和当地人推荐（3-5个）
            - 免费或低成本活动（3-4个）
            - 文化体验（2-3个）
            - 户外活动（2-3个）
            - 适合家庭的选择（2-3个）

            总共提供15-20个景点，涵盖不同兴趣和预算。
            请确保所有景点名称和描述都使用中文。
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse the AI response into structured data
            attractions = self._parse_attractions_response(response.text, destination)
            
            return attractions
            
        except Exception as e:
            logger.error(f"Error generating attractions with AI: {str(e)}")
            return self._get_sample_attractions(destination)
    
    def _parse_attractions_response(self, ai_response: str, destination: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured attraction data."""
        try:
            import re
            
            # Try to parse the actual AI response
            attractions = []
            
            if ai_response and len(ai_response) > 100:
                # Split the response into sections for each attraction
                # Look for numbered items or clear attraction separators
                attraction_sections = self._split_ai_response_into_attractions(ai_response)
                
                for i, section in enumerate(attraction_sections[:20]):  # Limit to 20 attractions
                    try:
                        attraction = self._parse_single_attraction(section, destination, i)
                        if attraction:
                            attractions.append(attraction)
                    except Exception as e:
                        logger.warning(f"Error parsing attraction section {i}: {str(e)}")
                        continue
            
            # If we couldn't parse enough attractions from AI response, supplement with defaults
            if len(attractions) < 6:
                logger.info(f"Only parsed {len(attractions)} attractions from AI, supplementing with defaults")
                default_attractions = self._get_default_attractions(destination)
                
                # Add default attractions that don't conflict with parsed ones
                existing_names = {attr.get('name', '').lower() for attr in attractions}
                for default_attr in default_attractions:
                    if default_attr.get('name', '').lower() not in existing_names:
                        attractions.append(default_attr)
                        if len(attractions) >= 15:  # Reasonable limit
                            break
            
            # Ensure all attractions have required fields
            attractions = [self._validate_and_complete_attraction(attr, destination) for attr in attractions]
            
            logger.info(f"Successfully parsed {len(attractions)} attractions from AI response")
            return attractions
            
        except Exception as e:
            logger.error(f"Error parsing attractions response: {str(e)}")
            return self._get_default_attractions(destination)
    
    def _split_ai_response_into_attractions(self, ai_response: str) -> List[str]:
        """Split AI response into individual attraction sections."""
        try:
            # Try different splitting patterns
            sections = []
            
            # Pattern 1: Numbered list (1., 2., etc.)
            numbered_pattern = r'\d+\.\s*([^0-9]+?)(?=\d+\.|$)'
            numbered_matches = re.findall(numbered_pattern, ai_response, re.DOTALL)
            if len(numbered_matches) >= 3:
                sections = numbered_matches
            
            # Pattern 2: Double newlines as separators
            elif '\n\n' in ai_response:
                sections = [s.strip() for s in ai_response.split('\n\n') if len(s.strip()) > 50]
            
            # Pattern 3: Single newlines with attraction names
            elif len(sections) < 3:
                lines = ai_response.split('\n')
                current_section = []
                for line in lines:
                    line = line.strip()
                    if line and (any(keyword in line.lower() for keyword in ['name:', 'attraction:', '**']) or 
                               (len(current_section) > 0 and len(line) > 30)):
                        if current_section:
                            sections.append('\n'.join(current_section))
                        current_section = [line]
                    elif line:
                        current_section.append(line)
                
                if current_section:
                    sections.append('\n'.join(current_section))
            
            # Filter out very short sections
            sections = [s for s in sections if len(s.strip()) > 30]
            
            logger.info(f"Split AI response into {len(sections)} attraction sections")
            return sections
            
        except Exception as e:
            logger.error(f"Error splitting AI response: {str(e)}")
            return [ai_response]  # Return whole response as single section
    
    def _parse_single_attraction(self, section: str, destination: str, index: int) -> Dict[str, Any]:
        """Parse a single attraction section from AI response."""
        try:
            import re
            
            attraction = {}
            
            # Clean the section first - remove markdown formatting and fix escape characters
            cleaned_section = self._clean_text_content(section)
            
            # Extract name (look for patterns like "景点名称：", "**Name**", or first line)
            name_patterns = [
                r'景点名称[：:]\s*([^\n]+)',
                r'名称[：:]\s*([^\n]+)',
                r'\*\*景点名称[：:]\s*([^*]+)\*\*',
                r'\*\*([^*]+)\*\*',
                r'^([^:\n]+)(?:\n|:)',
                r'(\d+\.\s*)?([^:\n]+)'
            ]
            
            name = None
            for pattern in name_patterns:
                match = re.search(pattern, cleaned_section, re.IGNORECASE | re.MULTILINE)
                if match:
                    # Safely get the last available group
                    try:
                        name = match.group(-1).strip() if match.groups() else match.group(0).strip()
                    except IndexError:
                        name = match.group(0).strip()  # Fallback to entire match
                    name = re.sub(r'^\d+\.\s*', '', name)  # Remove numbering
                    name = self._clean_text_content(name)  # Clean the name
                    if len(name) > 3 and len(name) < 100:  # Reasonable name length
                        break
            
            if not name:
                name = f'{destination}景点{index + 1}'
            
            attraction['name'] = name
            
            # Extract description - look for "简要描述" or use cleaned content
            desc_patterns = [
                r'简要描述[：:]\s*([^\n*]+(?:\n[^\n*:]+)*)',
                r'描述[：:]\s*([^\n*]+(?:\n[^\n*:]+)*)',
                r'(?:' + re.escape(name) + r'[^\n]*\n)([^\n:*]+(?:\n[^\n:*]+)*)'
            ]
            
            description = None
            for pattern in desc_patterns:
                match = re.search(pattern, cleaned_section, re.IGNORECASE | re.DOTALL)
                if match:
                    try:
                        description = match.group(1).strip() if match.groups() else match.group(0).strip()
                    except IndexError:
                        description = match.group(0).strip()
                    description = self._clean_text_content(description)
                    if len(description) > 20:
                        break
            
            if not description:
                # Use first substantial paragraph as description
                lines = [line.strip() for line in cleaned_section.split('\n') if line.strip()]
                for line in lines[1:]:  # Skip first line (likely the name)
                    cleaned_line = self._clean_text_content(line)
                    if len(cleaned_line) > 30 and ':' not in cleaned_line[:20] and not cleaned_line.startswith('*'):
                        description = cleaned_line
                        break
            
            attraction['description'] = description or f'{destination}的著名景点，值得一游。'
            
            # Extract other fields using regex patterns
            field_patterns = {
                'category': r'类别[：:]\s*([^\n*]+)',
                'duration': r'(?:预计游览时长|游览时长|时长)[：:]\s*([^\n*]+)',
                'entrance_fee': r'(?:门票价格|门票|价格)[：:]\s*([^\n*]+)',
                'best_time': r'最佳游览时间[：:]\s*([^\n*]+)',
                'difficulty': r'难度等级[：:]\s*([^\n*]+)',
                'rating': r'(?:rating|score|评分)[：:]\s*([^\n*]+)'
            }
            
            for field, pattern in field_patterns.items():
                match = re.search(pattern, cleaned_section, re.IGNORECASE)
                if match:
                    try:
                        value = match.group(1).strip() if match.groups() else match.group(0).strip()
                    except IndexError:
                        value = match.group(0).strip()
                    
                    value = self._clean_text_content(value)
                    
                    if field == 'entrance_fee':
                        # Extract numeric value from fee
                        fee_match = re.search(r'(\d+(?:\.\d+)?)', value)
                        attraction[field] = float(fee_match.group(1)) if fee_match else 0
                    elif field == 'rating':
                        # Extract numeric rating
                        rating_match = re.search(r'(\d+(?:\.\d+)?)', value)
                        attraction[field] = float(rating_match.group(1)) if rating_match else 4.0
                    else:
                        attraction[field] = value
            
            return attraction
            
        except Exception as e:
            logger.error(f"Error parsing single attraction: {str(e)}")
            return None
    
    def _clean_text_content(self, text: str) -> str:
        """Clean text content by removing markdown formatting and fixing escape characters."""
        if not text:
            return ""
        
        import html
        import re
        
        # HTML decode
        text = html.unescape(text)
        
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove **bold**
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Remove *italic*
        text = re.sub(r'`([^`]+)`', r'\1', text)        # Remove `code`
        
        # Remove bullet points and list markers
        text = re.sub(r'^\s*[\*\-\+]\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s*', '', text, flags=re.MULTILINE)
        
        # Handle escape characters
        text = text.replace('\\n', '\n')
        text = text.replace('\\t', '\t')
        text = text.replace('\\r', '\r')
        text = text.replace('\\"', '"')
        text = text.replace("\\'", "'")
        text = text.replace('\\\\', '\\')
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Handle special HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&', '&')
        text = text.replace('<', '<')
        text = text.replace('>', '>')
        text = text.replace('"', '"')
        
        return text
    
    def _get_default_attractions(self, destination: str) -> List[Dict[str, Any]]:
        """Get default attractions when AI parsing fails or needs supplementing."""
        try:
            # Try to generate better default attractions using AI
            fallback_prompt = f"""
            请为{destination}生成6个真实的景点。如果知道实际地名请使用，否则创建合理的名称。
            请为每个景点提供：景点名称（中文）、描述（1-2句话，中文）、类别、游览时长、门票价格（数字）、评分（1-5分）。
            请用简单列表格式，景点之间清楚分隔。
            确保所有内容都使用中文。
            """
            
            try:
                response = self.model.generate_content(fallback_prompt)
                if response and response.text:
                    # Try to parse the fallback response
                    fallback_attractions = self._parse_attractions_response(response.text, destination)
                    if len(fallback_attractions) >= 3:
                        return fallback_attractions[:6]  # Return up to 6 attractions
            except Exception as e:
                logger.warning(f"Failed to generate AI fallback attractions: {str(e)}")
            
            # If AI fails, return minimal hardcoded fallbacks
            return [
                {
                    'name': f'{destination}历史街区',
                    'description': f'探索{destination}的历史中心，这里有独特的建筑风格和深厚的文化底蕴，是了解当地历史文化的绝佳去处。',
                    'category': '历史文化',
                    'duration': '3-4小时',
                    'entrance_fee': 0,
                    'best_time': '上午或傍晚',
                    'difficulty': '简单',
                    'age_suitability': '适合所有年龄',
                    'photography': '允许',
                    'accessibility': '大部分区域可达',
                    'rating': 4.5,
                    'highlights': ['历史建筑', '文化遗址', '步行游览'],
                    'search_keywords': [f'{destination} 历史', f'{destination} 古城', f'{destination} 文化遗产']
                },
                {
                    'name': f'{destination}文化博物馆',
                    'description': f'展示{destination}艺术、历史和文化遗产的当地博物馆，收藏丰富，是深入了解当地文化的重要场所。',
                    'category': '文化教育',
                    'duration': '2-3小时',
                    'entrance_fee': 12,
                    'best_time': '任何时间',
                    'difficulty': '简单',
                    'age_suitability': '适合所有年龄',
                    'photography': '限制拍照',
                    'accessibility': '完全无障碍',
                    'rating': 4.2,
                    'highlights': ['当地艺术', '文化展览', '历史文物'],
                    'search_keywords': [f'{destination} 博物馆', f'{destination} 文化', f'{destination} 艺术']
                },
                {
                    'name': f'{destination}中心广场',
                    'description': f'{destination}的中心聚集地，充满当地生活气息，周围有商店和咖啡馆，是体验当地文化的好地方。',
                    'category': '文化休闲',
                    'duration': '1-2小时',
                    'entrance_fee': 0,
                    'best_time': '傍晚',
                    'difficulty': '简单',
                    'age_suitability': '适合所有年龄',
                    'photography': '允许',
                    'accessibility': '完全无障碍',
                    'rating': 4.3,
                    'highlights': ['当地氛围', '人文观察', '周边餐饮'],
                    'search_keywords': [f'{destination} 广场', f'{destination} 中心', f'{destination} 市中心']
                }
            ]
        except Exception as e:
            logger.error(f"Error in _get_default_attractions: {str(e)}")
            return []
    
    def _validate_and_complete_attraction(self, attraction: Dict[str, Any], destination: str) -> Dict[str, Any]:
        """Validate and complete attraction data with defaults for missing fields."""
        try:
            # Ensure required fields exist with defaults
            defaults = {
                'name': f'{destination} Attraction',
                'description': f'A notable attraction in {destination}.',
                'category': 'General',
                'duration': '2-3 hours',
                'entrance_fee': 0,
                'best_time': 'Any time',
                'difficulty': 'Easy',
                'age_suitability': 'All ages',
                'photography': 'Yes',
                'accessibility': 'Check locally',
                'rating': 4.0,
                'highlights': ['Worth visiting'],
                'search_keywords': [f'{destination} attraction']
            }
            
            # Fill in missing fields
            for key, default_value in defaults.items():
                if key not in attraction or not attraction[key]:
                    attraction[key] = default_value
            
            # Validate and clean data
            if isinstance(attraction.get('entrance_fee'), str):
                # Try to extract number from string
                import re
                fee_match = re.search(r'(\d+(?:\.\d+)?)', str(attraction['entrance_fee']))
                try:
                    attraction['entrance_fee'] = float(fee_match.group(1)) if fee_match and fee_match.groups() else 0
                except (IndexError, ValueError):
                    attraction['entrance_fee'] = 0
            
            if isinstance(attraction.get('rating'), str):
                # Try to extract rating from string
                import re
                rating_match = re.search(r'(\d+(?:\.\d+)?)', str(attraction['rating']))
                try:
                    attraction['rating'] = float(rating_match.group(1)) if rating_match and rating_match.groups() else 4.0
                except (IndexError, ValueError):
                    attraction['rating'] = 4.0
            
            # Ensure rating is within valid range
            if not isinstance(attraction.get('rating'), (int, float)) or attraction['rating'] < 1 or attraction['rating'] > 5:
                attraction['rating'] = 4.0
            
            # Ensure entrance_fee is numeric
            if not isinstance(attraction.get('entrance_fee'), (int, float)):
                attraction['entrance_fee'] = 0
            
            return attraction
            
        except Exception as e:
            logger.error(f"Error validating attraction: {str(e)}")
            return {
                'name': f'{destination} Attraction',
                'description': f'A notable attraction in {destination}.',
                'category': 'General',
                'duration': '2-3 hours',
                'entrance_fee': 0,
                'rating': 4.0
            }
    
    def _enhance_attraction_data(self, attractions: List[Dict[str, Any]], budget: float) -> List[Dict[str, Any]]:
        """Enhance attraction data with additional details."""
        try:
            activities_budget = budget * 0.15
            daily_activities_budget = activities_budget / 7  # Assuming 7 days
            
            enhanced_attractions = []
            
            for attraction in attractions:
                # Add budget-related information
                entrance_fee = attraction.get('entrance_fee', 0)
                
                enhanced_attraction = attraction.copy()
                enhanced_attraction.update({
                    'budget_friendly': entrance_fee <= daily_activities_budget * 0.5,
                    'premium_experience': entrance_fee > daily_activities_budget,
                    'estimated_total_cost': entrance_fee + (entrance_fee * 0.2),  # Include extras
                    'booking_required': entrance_fee > 20,  # Assume expensive attractions need booking
                    'group_discounts': entrance_fee > 10,  # Assume group discounts for paid attractions
                    'seasonal_availability': 'Year-round',  # Default, could be enhanced
                    'nearby_amenities': ['Restrooms', 'Parking', 'Food options'],
                    'tips': self._generate_attraction_tips(attraction)
                })
                
                enhanced_attractions.append(enhanced_attraction)
            
            # Sort by rating and budget-friendliness
            enhanced_attractions.sort(key=lambda x: (x.get('rating', 0), -x.get('entrance_fee', 0)), reverse=True)
            
            return enhanced_attractions
            
        except Exception as e:
            logger.error(f"Error enhancing attraction {str(e)}")
            return attractions
    
    def _generate_attraction_tips(self, attraction: Dict[str, Any]) -> List[str]:
        """Generate practical tips for visiting an attraction."""
        tips = []
        
        # General tips based on attraction properties
        if attraction.get('entrance_fee', 0) > 0:
            tips.append("Book tickets online in advance for potential discounts")
        
        if attraction.get('category') == 'Historical':
            tips.append("Consider hiring a local guide for deeper insights")
        
        if attraction.get('photography') == 'Restricted':
            tips.append("Check photography rules before your visit")
        
        if attraction.get('best_time') == 'Morning':
            tips.append("Arrive early to avoid crowds and enjoy cooler weather")
        
        if attraction.get('difficulty') == 'Challenging':
            tips.append("Wear comfortable shoes and bring water")
        
        # Add default tips if none generated
        if not tips:
            tips = [
                "Check opening hours before visiting",
                "Bring comfortable walking shoes",
                "Allow extra time for exploration"
            ]
        
        return tips[:3]  # Return top 3 tips
    
    def _get_sample_attractions(self, destination: str) -> List[Dict[str, Any]]:
        """Get sample attractions when AI generation fails."""
        return [
            {
                'name': f'{destination}主广场',
                'description': f'{destination}的中心广场，具有历史意义和浓厚的当地生活氛围，是体验当地文化的理想场所。',
                'category': '历史文化',
                'duration': '1-2小时',
                'entrance_fee': 0,
                'rating': 4.2,
                'highlights': ['历史建筑', '当地文化']
            },
            {
                'name': f'{destination}文化中心',
                'description': f'{destination}当地艺术和文化活动的中心，经常举办各种展览和文化活动。',
                'category': '文化教育',
                'duration': '2-3小时',
                'entrance_fee': 10,
                'rating': 4.0,
                'highlights': ['艺术展览', '文化活动']
            },
            {
                'name': f'{destination}观景台',
                'description': f'欣赏{destination}城市和周边风景的绝佳观景点，景色优美，适合拍照留念。',
                'category': '自然风光',
                'duration': '1小时',
                'entrance_fee': 5,
                'rating': 4.4,
                'highlights': ['全景视野', '摄影胜地']
            }
        ]
    
    
    def _get_fallback_attractions(self, destination: str, budget: float) -> List[Dict[str, Any]]:
        """Get fallback attractions when all else fails."""
        try:
            return [
                {
                    'name': f'{destination}城市观光游',
                    'description': f'全面的{destination}城市观光游，涵盖主要景点和地标建筑，是初次到访的理想选择。',
                    'category': '综合观光',
                    'duration': '4-6小时',
                    'entrance_fee': 30,
                    'best_time': '上午',
                    'difficulty': '简单',
                    'age_suitability': '适合所有年龄',
                    'photography': '允许',
                    'accessibility': '因地点而异',
                    'rating': 4.0,
                    'highlights': ['城市概览', '多个景点', '导游服务'],
                    'budget_friendly': True,
                    'tips': ['提前预订', '穿舒适的鞋子', '携带相机']
                }
            ]
            
        except Exception as e:
            logger.error(f"Error creating fallback attractions: {str(e)}")
            return []
