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
    
    def __init__(self):
        """Initialize the attraction service."""
        # Initialize Gemini for attraction data generation
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Initialize image handler for attraction images
        self.image_handler = ImageHandler()
        
        logger.info("Attraction Service initialized")
    
    def get_attractions(self, destination: str, budget: float) -> List[Dict[str, Any]]:
        """
        Get attractions and points of interest for a destination.
        
        Note: Real-time attraction data is now handled by Google ADK MCP tools
        at the agent level. This service provides AI-generated attractions that
        can be enhanced with real MCP data when the agent uses MCP tools.
        
        Args:
            destination: Target destination
            budget: Total budget for activities
            
        Returns:
            List of attraction data
        """
        try:
            logger.info(f"Getting attractions for {destination}")
            
            # Generate comprehensive AI-based attractions
            # Real-time MCP data integration happens at the agent level
            enhanced_attractions = self._generate_attractions_with_ai(destination, budget)
            
            # Enhance with additional details
            final_attractions = self._enhance_attraction_data(enhanced_attractions, budget)
            
            # Add images to attractions
            try:
                logger.info(f"Adding images to {len(final_attractions)} attractions for {destination}")
                attractions_with_images = self.image_handler.get_attraction_images(destination, final_attractions)
                
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
            
            # Extract name (look for patterns like "Name:", "**Name**", or first line)
            name_patterns = [
                r'(?:name|attraction):\s*([^\n]+)',
                r'\*\*([^*]+)\*\*',
                r'^([^:\n]+)(?:\n|:)',
                r'(\d+\.\s*)?([^:\n]+)'
            ]
            
            name = None
            for pattern in name_patterns:
                match = re.search(pattern, section, re.IGNORECASE | re.MULTILINE)
                if match:
                    # Safely get the last available group
                    try:
                        name = match.group(-1).strip() if match.groups() else match.group(0).strip()
                    except IndexError:
                        name = match.group(0).strip()  # Fallback to entire match
                    name = re.sub(r'^\d+\.\s*', '', name)  # Remove numbering
                    if len(name) > 5 and len(name) < 100:  # Reasonable name length
                        break
            
            if not name:
                name = f'{destination} Attraction {index + 1}'
            
            attraction['name'] = name
            
            # Extract description (look for description field or use remaining text)
            desc_patterns = [
                r'(?:description|about):\s*([^\n]+(?:\n[^\n:]+)*)',
                r'(?:' + re.escape(name) + r'[^\n]*\n)([^\n:]+(?:\n[^\n:]+)*)'
            ]
            
            description = None
            for pattern in desc_patterns:
                match = re.search(pattern, section, re.IGNORECASE | re.DOTALL)
                if match:
                    try:
                        description = match.group(1).strip() if match.groups() else match.group(0).strip()
                    except IndexError:
                        description = match.group(0).strip()
                    if len(description) > 20:
                        break
            
            if not description:
                # Use first substantial paragraph as description
                lines = [line.strip() for line in section.split('\n') if line.strip()]
                for line in lines[1:]:  # Skip first line (likely the name)
                    if len(line) > 30 and ':' not in line[:20]:
                        description = line
                        break
            
            attraction['description'] = description or f'A notable attraction in {destination} worth visiting.'
            
            # Extract other fields using regex patterns
            field_patterns = {
                'category': r'(?:category|type):\s*([^\n]+)',
                'duration': r'(?:duration|time|visit):\s*([^\n]+)',
                'entrance_fee': r'(?:fee|price|cost|entrance):\s*([^\n]+)',
                'best_time': r'(?:best time|when):\s*([^\n]+)',
                'difficulty': r'(?:difficulty|level):\s*([^\n]+)',
                'rating': r'(?:rating|score):\s*([^\n]+)'
            }
            
            for field, pattern in field_patterns.items():
                match = re.search(pattern, section, re.IGNORECASE)
                if match:
                    try:
                        value = match.group(1).strip() if match.groups() else match.group(0).strip()
                    except IndexError:
                        value = match.group(0).strip()
                    
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
