"""
Travel Planner Agent
Core planning logic for generating optimized travel itineraries
"""

import os
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
from ..utils.budget_calculator import BudgetCalculator

logger = logging.getLogger(__name__)

class TravelPlannerAgent:
    """Agent responsible for generating intelligent travel plans."""
    
    def __init__(self):
        """Initialize the travel planner."""
        self.budget_calculator = BudgetCalculator()
        
        # Initialize Gemini for intelligent planning
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Date mappings for Chinese relative dates
        self.date_mappings = {
            "今天": 0,
            "明天": 1,
            "后天": 2,
            "大后天": 3
        }
        
        logger.info("Travel Planner Agent initialized")
    
    def parse_date_input(self, date_input: str) -> str:
        """
        Parse date input and convert relative dates to absolute dates.
        
        Args:
            date_input: Date input (can be relative like "今天", "明天" or absolute like "2025-07-27")
            
        Returns:
            Standardized date string in YYYY-MM-DD format
        """
        try:
            # Get current system date
            today = datetime.now().date()
            
            # Handle Chinese relative dates
            if date_input in self.date_mappings:
                target_date = today + timedelta(days=self.date_mappings[date_input])
                return target_date.strftime('%Y-%m-%d')
            
            # Handle absolute dates in various formats
            date_patterns = [
                r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
                r'(\d{4})/(\d{1,2})/(\d{1,2})',  # YYYY/MM/DD
                r'(\d{1,2})-(\d{1,2})-(\d{4})',  # DD-MM-YYYY
                r'(\d{1,2})/(\d{1,2})/(\d{4})'   # DD/MM/YYYY
            ]
            
            for pattern in date_patterns:
                match = re.match(pattern, date_input.strip())
                if match:
                    if len(match.group(1)) == 4:  # YYYY first
                        year, month, day = match.groups()
                    else:  # DD first
                        day, month, year = match.groups()
                    
                    parsed_date = datetime(int(year), int(month), int(day)).date()
                    
                    # Validate date is not in the past
                    if parsed_date < today:
                        logger.warning(f"Date {date_input} is in the past, using today instead")
                        return today.strftime('%Y-%m-%d')
                    
                    return parsed_date.strftime('%Y-%m-%d')
            
            # If no pattern matches, try to parse as-is
            try:
                parsed_date = datetime.strptime(date_input, '%Y-%m-%d').date()
                if parsed_date < today:
                    logger.warning(f"Date {date_input} is in the past, using today instead")
                    return today.strftime('%Y-%m-%d')
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                logger.warning(f"Could not parse date {date_input}, using today")
                return today.strftime('%Y-%m-%d')
                
        except Exception as e:
            logger.error(f"Error parsing date {date_input}: {str(e)}")
            return datetime.now().date().strftime('%Y-%m-%d')

    def generate_plans(
        self,
        travel_data: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate multiple travel plan options.
        
        Args:
            travel_data: Collected travel data
            preferences: User preferences
            
        Returns:
            Dict containing generated travel plans
        """
        try:
            logger.info("Generating travel plans")
            
            # Extract key information
            destination_info = travel_data.get('destination_info', {})
            budget_estimates = travel_data.get('budget_estimates', {})
            attractions = travel_data.get('attractions', [])
            accommodations = travel_data.get('accommodations', [])
            dining = travel_data.get('dining', [])
            weather_data = travel_data.get('weather_data', {})
            
            # Generate multiple plan scenarios
            plans = []
            
            # Economic Plan
            economic_plan = self._generate_economic_plan(
                travel_data, preferences
            )
            if economic_plan:
                plans.append(economic_plan)
            
            # Comfort Plan
            comfort_plan = self._generate_comfort_plan(
                travel_data, preferences
            )
            if comfort_plan:
                plans.append(comfort_plan)
            
            # Custom Plan (if preferences specify)
            if preferences.get('custom_requirements'):
                custom_plan = self._generate_custom_plan(
                    travel_data, preferences
                )
                if custom_plan:
                    plans.append(custom_plan)
            
            return {
                'success': True,
                'plans': plans,
                'generation_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating travel plans: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'plans': []
            }
    
    def _generate_economic_plan(
        self,
        travel_data: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate a budget-focused travel plan."""
        try:
            budget_estimates = travel_data.get('budget_estimates', {})
            total_budget = budget_estimates.get('total_budget', 0)
            
            # Reduce budget by 20% for economic plan
            economic_budget = total_budget * 0.8
            
            plan = {
                'plan_type': 'Economic',
                'description': 'Budget-friendly travel plan focusing on value and essential experiences',
                'total_budget': economic_budget,
                'budget_allocation': self._calculate_budget_allocation(economic_budget, 'economic'),
                'itinerary': self._generate_itinerary(travel_data, economic_budget, 'economic'),
                'accommodations': self._select_accommodations(
                    travel_data.get('accommodations', []), 
                    economic_budget * 0.35, 
                    'budget'
                ),
                'dining_plan': self._create_dining_plan(
                    travel_data.get('dining', []), 
                    economic_budget * 0.20, 
                    'budget'
                ),
                'transportation': self._plan_transportation(
                    travel_data.get('transportation', {}), 
                    economic_budget * 0.30, 
                    'budget'
                ),
                'tips': [
                    'Book accommodations in advance for better rates',
                    'Use public transportation when possible',
                    'Try local street food for authentic and affordable meals',
                    'Look for free walking tours and activities',
                    'Visit attractions during off-peak hours for discounts'
                ]
            }
            
            return plan
            
        except Exception as e:
            logger.error(f"Error generating economic plan: {str(e)}")
            return None
    
    def _generate_comfort_plan(
        self,
        travel_data: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate a comfort-focused travel plan."""
        try:
            budget_estimates = travel_data.get('budget_estimates', {})
            total_budget = budget_estimates.get('total_budget', 0)
            
            # Use full budget for comfort plan
            comfort_budget = total_budget
            
            plan = {
                'plan_type': 'Comfort',
                'description': 'Comfortable travel plan with premium experiences and convenience',
                'total_budget': comfort_budget,
                'budget_allocation': self._calculate_budget_allocation(comfort_budget, 'comfort'),
                'itinerary': self._generate_itinerary(travel_data, comfort_budget, 'comfort'),
                'accommodations': self._select_accommodations(
                    travel_data.get('accommodations', []), 
                    comfort_budget * 0.35, 
                    'comfort'
                ),
                'dining_plan': self._create_dining_plan(
                    travel_data.get('dining', []), 
                    comfort_budget * 0.20, 
                    'comfort'
                ),
                'transportation': self._plan_transportation(
                    travel_data.get('transportation', {}), 
                    comfort_budget * 0.30, 
                    'comfort'
                ),
                'tips': [
                    'Book premium accommodations with good amenities',
                    'Consider private transportation for convenience',
                    'Make reservations at recommended restaurants',
                    'Purchase skip-the-line tickets for popular attractions',
                    'Consider guided tours for deeper cultural insights'
                ]
            }
            
            return plan
            
        except Exception as e:
            logger.error(f"Error generating comfort plan: {str(e)}")
            return None
    
    def _generate_custom_plan(
        self,
        travel_data: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate a custom plan based on specific preferences."""
        try:
            # This would be enhanced based on specific user preferences
            # For now, create a balanced plan
            budget_estimates = travel_data.get('budget_estimates', {})
            total_budget = budget_estimates.get('total_budget', 0)
            
            plan = {
                'plan_type': 'Custom',
                'description': 'Personalized travel plan based on your specific preferences',
                'total_budget': total_budget,
                'budget_allocation': self._calculate_budget_allocation(total_budget, 'balanced'),
                'itinerary': self._generate_itinerary(travel_data, total_budget, 'balanced'),
                'accommodations': self._select_accommodations(
                    travel_data.get('accommodations', []), 
                    total_budget * 0.35, 
                    'mid-range'
                ),
                'dining_plan': self._create_dining_plan(
                    travel_data.get('dining', []), 
                    total_budget * 0.20, 
                    'varied'
                ),
                'transportation': self._plan_transportation(
                    travel_data.get('transportation', {}), 
                    total_budget * 0.30, 
                    'mixed'
                ),
                'special_features': self._add_custom_features(preferences),
                'tips': [
                    'Plan customized based on your preferences',
                    'Flexible itinerary allows for spontaneous discoveries',
                    'Balance of planned activities and free time',
                    'Mix of popular attractions and local experiences'
                ]
            }
            
            return plan
            
        except Exception as e:
            logger.error(f"Error generating custom plan: {str(e)}")
            return None
    
    def _calculate_budget_allocation(self, total_budget: float, plan_type: str) -> Dict[str, Any]:
        """Calculate budget allocation for different categories."""
        try:
            if plan_type == 'economic':
                # More budget for accommodation and transport, less for activities
                allocation = {
                    'transportation': {'amount': total_budget * 0.32, 'percentage': 32},
                    'accommodation': {'amount': total_budget * 0.38, 'percentage': 38},
                    'dining': {'amount': total_budget * 0.18, 'percentage': 18},
                    'activities': {'amount': total_budget * 0.12, 'percentage': 12}
                }
            elif plan_type == 'comfort':
                # More budget for activities and dining
                allocation = {
                    'transportation': {'amount': total_budget * 0.28, 'percentage': 28},
                    'accommodation': {'amount': total_budget * 0.32, 'percentage': 32},
                    'dining': {'amount': total_budget * 0.22, 'percentage': 22},
                    'activities': {'amount': total_budget * 0.18, 'percentage': 18}
                }
            else:  # balanced
                allocation = {
                    'transportation': {'amount': total_budget * 0.30, 'percentage': 30},
                    'accommodation': {'amount': total_budget * 0.35, 'percentage': 35},
                    'dining': {'amount': total_budget * 0.20, 'percentage': 20},
                    'activities': {'amount': total_budget * 0.15, 'percentage': 15}
                }
            
            return allocation
            
        except Exception as e:
            logger.error(f"Error calculating budget allocation: {str(e)}")
            return {}
    
    def _generate_itinerary(
        self,
        travel_data: Dict[str, Any],
        budget: float,
        plan_type: str
    ) -> List[Dict[str, Any]]:
        """Generate day-by-day itinerary."""
        try:
            # Use AI to generate intelligent itinerary
            destination = travel_data.get('destination_info', {}).get('name', 'Destination')
            attractions = travel_data.get('attractions', [])
            weather_data = travel_data.get('weather_data', {})
            
            prompt = f"""
            Create a detailed day-by-day itinerary for {destination} with the following considerations:
            
            Plan Type: {plan_type}
            Budget: {budget}
            Available Attractions: {len(attractions)} attractions
            
            For each day, provide:
            1. Morning activities (9:00-12:00)
            2. Afternoon activities (13:00-17:00)
            3. Evening activities (18:00-21:00)
            4. Recommended restaurants for each meal
            5. Transportation between locations
            6. Estimated costs and time requirements
            7. Weather considerations
            8. Alternative indoor activities if needed
            
            Create a 7-day itinerary that balances must-see attractions with local experiences.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse the AI response into structured itinerary
            itinerary = self._parse_itinerary_response(response.text, plan_type)
            
            return itinerary
            
        except Exception as e:
            logger.error(f"Error generating itinerary: {str(e)}")
            return self._create_fallback_itinerary(plan_type)
    
    def _parse_itinerary_response(self, response_text: str, plan_type: str) -> List[Dict[str, Any]]:
        """Parse AI-generated itinerary into structured format."""
        try:
            # Simple parsing - can be enhanced with more sophisticated NLP
            days = []
            
            # Create sample structured itinerary
            for day_num in range(1, 8):  # 7 days
                day_plan = {
                    'day': day_num,
                    'date': f"Day {day_num}",
                    'theme': f"Explore & Discover - Day {day_num}",
                    'activities': {
                        'morning': {
                            'time': '09:00-12:00',
                            'activity': f'Morning Attraction Visit - Day {day_num}',
                            'location': 'Main Tourist Area',
                            'estimated_cost': 50 if plan_type == 'comfort' else 30,
                            'duration': '3 hours',
                            'notes': 'Start early to avoid crowds'
                        },
                        'afternoon': {
                            'time': '13:00-17:00',
                            'activity': f'Afternoon Cultural Experience - Day {day_num}',
                            'location': 'Cultural District',
                            'estimated_cost': 40 if plan_type == 'comfort' else 25,
                            'duration': '4 hours',
                            'notes': 'Include lunch break'
                        },
                        'evening': {
                            'time': '18:00-21:00',
                            'activity': f'Evening Dining & Leisure - Day {day_num}',
                            'location': 'Entertainment District',
                            'estimated_cost': 60 if plan_type == 'comfort' else 35,
                            'duration': '3 hours',
                            'notes': 'Enjoy local nightlife'
                        }
                    },
                    'meals': {
                        'breakfast': {'location': 'Hotel/Local Cafe', 'cost': 15},
                        'lunch': {'location': 'Local Restaurant', 'cost': 25},
                        'dinner': {'location': 'Recommended Restaurant', 'cost': 45}
                    },
                    'transportation': {
                        'method': 'Public Transit' if plan_type == 'economic' else 'Mixed',
                        'estimated_cost': 10 if plan_type == 'economic' else 20
                    },
                    'total_daily_cost': 200 if plan_type == 'comfort' else 140
                }
                
                days.append(day_plan)
            
            return days
            
        except Exception as e:
            logger.error(f"Error parsing itinerary response: {str(e)}")
            return self._create_fallback_itinerary(plan_type)
    
    def _create_fallback_itinerary(self, plan_type: str) -> List[Dict[str, Any]]:
        """Create a basic fallback itinerary."""
        return [
            {
                'day': 1,
                'date': 'Day 1',
                'theme': 'Arrival & City Overview',
                'activities': {
                    'morning': {
                        'activity': 'Arrival and Check-in',
                        'estimated_cost': 0,
                        'duration': '2 hours'
                    },
                    'afternoon': {
                        'activity': 'City Walking Tour',
                        'estimated_cost': 30,
                        'duration': '3 hours'
                    },
                    'evening': {
                        'activity': 'Welcome Dinner',
                        'estimated_cost': 50,
                        'duration': '2 hours'
                    }
                },
                'total_daily_cost': 80
            }
        ]
    
    def _select_accommodations(
        self,
        accommodations: List[Dict[str, Any]],
        budget: float,
        preference: str
    ) -> List[Dict[str, Any]]:
        """Select appropriate accommodations based on budget and preference."""
        try:
            if not accommodations:
                # Create sample accommodations
                accommodations = [
                    {
                        'name': 'Budget Hotel',
                        'type': 'Hotel',
                        'price_per_night': budget * 0.15,
                        'rating': 3.5,
                        'location': 'City Center',
                        'amenities': ['WiFi', 'Breakfast']
                    },
                    {
                        'name': 'Comfort Inn',
                        'type': 'Hotel',
                        'price_per_night': budget * 0.25,
                        'rating': 4.0,
                        'location': 'Tourist District',
                        'amenities': ['WiFi', 'Breakfast', 'Gym', 'Pool']
                    },
                    {
                        'name': 'Luxury Resort',
                        'type': 'Resort',
                        'price_per_night': budget * 0.40,
                        'rating': 4.8,
                        'location': 'Premium Area',
                        'amenities': ['WiFi', 'Breakfast', 'Spa', 'Concierge', 'Pool', 'Gym']
                    }
                ]
            
            # Filter based on preference and budget
            daily_accommodation_budget = budget / 7  # Assuming 7 nights
            
            suitable_accommodations = []
            for acc in accommodations:
                price = acc.get('price_per_night', 0)
                if preference == 'budget' and price <= daily_accommodation_budget * 0.8:
                    suitable_accommodations.append(acc)
                elif preference == 'comfort' and price <= daily_accommodation_budget * 1.2:
                    suitable_accommodations.append(acc)
                elif preference == 'mid-range' and price <= daily_accommodation_budget:
                    suitable_accommodations.append(acc)
            
            return suitable_accommodations[:3]  # Return top 3 options
            
        except Exception as e:
            logger.error(f"Error selecting accommodations: {str(e)}")
            return []
    
    def _create_dining_plan(
        self,
        dining_options: List[Dict[str, Any]],
        budget: float,
        preference: str
    ) -> Dict[str, Any]:
        """Create a dining plan based on budget and preferences."""
        try:
            daily_food_budget = budget / 7  # 7 days
            
            plan = {
                'daily_budget': daily_food_budget,
                'meal_allocation': {
                    'breakfast': daily_food_budget * 0.2,
                    'lunch': daily_food_budget * 0.35,
                    'dinner': daily_food_budget * 0.45
                },
                'recommended_restaurants': dining_options[:5],  # Top 5 recommendations
                'food_experiences': [
                    'Try local street food',
                    'Visit traditional markets',
                    'Experience fine dining (if budget allows)',
                    'Join a food tour',
                    'Cook with locals (if available)'
                ],
                'dietary_considerations': [
                    'Vegetarian options available',
                    'Halal restaurants identified',
                    'Allergy-friendly establishments noted'
                ]
            }
            
            return plan
            
        except Exception as e:
            logger.error(f"Error creating dining plan: {str(e)}")
            return {}
    
    def _plan_transportation(
        self,
        transport_data: Dict[str, Any],
        budget: float,
        preference: str
    ) -> Dict[str, Any]:
        """Plan comprehensive transportation including self-driving, high-speed rail, and flights."""
        try:
            intercity_budget = budget * 0.6
            local_budget = budget * 0.4
            
            # Enhanced transportation planning with three main options
            transport_options = {
                'self_driving': {
                    'type': '自驾',
                    'estimated_cost': intercity_budget * 0.4,  # Usually cheaper
                    'duration': '根据距离而定',
                    'pros': ['完全自由', '门到门服务', '可随时停靠', '适合多人出行'],
                    'cons': ['需要驾照', '停车费用', '疲劳驾驶风险', '路况影响'],
                    'includes': {
                        'fuel_cost': intercity_budget * 0.2,
                        'tolls': intercity_budget * 0.1,
                        'parking': intercity_budget * 0.1,
                        'insurance': '建议购买旅行保险'
                    },
                    'tips': [
                        '提前规划路线和休息点',
                        '检查车辆状况',
                        '准备应急工具包',
                        '了解目的地停车情况'
                    ],
                    'best_for': '喜欢自由行程的旅客'
                },
                'high_speed_rail': {
                    'type': '高铁',
                    'estimated_cost': intercity_budget * 0.6,
                    'duration': '通常比普通火车快50%',
                    'pros': ['舒适快捷', '准点率高', '市中心到市中心', '环保选择'],
                    'cons': ['需要提前订票', '班次有限', '价格较高'],
                    'booking_info': {
                        'advance_booking': '建议提前7-30天预订',
                        'seat_types': ['二等座', '一等座', '商务座'],
                        'discounts': '学生、老人可享受优惠',
                        'refund_policy': '开车前可退票，收取手续费'
                    },
                    'tips': [
                        '使用12306官方APP订票',
                        '选择合适的座位等级',
                        '提前到达车站安检',
                        '携带身份证件'
                    ],
                    'best_for': '追求舒适和效率的旅客'
                },
                'airplane': {
                    'type': '飞机',
                    'estimated_cost': intercity_budget * 0.8,
                    'duration': '最快选择，但需考虑机场时间',
                    'pros': ['速度最快', '长距离首选', '多航班选择', '服务标准化'],
                    'cons': ['机场往返时间', '天气影响', '行李限制', '安检时间'],
                    'booking_info': {
                        'advance_booking': '建议提前2-8周预订获得最佳价格',
                        'airlines': '比较不同航空公司价格和服务',
                        'baggage': '了解行李政策避免额外费用',
                        'check_in': '提前网上值机选座'
                    },
                    'airport_transfer': {
                        'options': ['机场大巴', '地铁', '出租车', '网约车'],
                        'estimated_cost': local_budget * 0.2,
                        'tips': '预留充足的机场往返时间'
                    },
                    'tips': [
                        '比较不同预订平台价格',
                        '关注航班动态',
                        '提前2小时到达机场',
                        '考虑购买延误险'
                    ],
                    'best_for': '时间紧张或长距离旅行的旅客'
                }
            }
            
            # Local transportation planning
            local_transport = {
                'daily_budget': local_budget / 7,
                'options': {
                    'public_transport': {
                        'types': ['地铁', '公交', '轻轨'],
                        'cost': '经济实惠',
                        'coverage': '覆盖主要景点',
                        'tips': '购买交通卡享受优惠'
                    },
                    'taxi_rideshare': {
                        'services': ['出租车', '滴滴', '网约车'],
                        'cost': '中等价位',
                        'convenience': '门到门服务',
                        'tips': '使用APP叫车更方便'
                    },
                    'walking_cycling': {
                        'walkability': '市中心步行友好',
                        'bike_sharing': '共享单车可用',
                        'cost': '最经济',
                        'tips': '适合短距离和观光'
                    }
                }
            }
            
            # Recommendation based on preference
            if preference == 'economic':
                recommended = 'self_driving'
                reason = '自驾游成本相对较低，且自由度高'
            elif preference == 'comfort':
                recommended = 'high_speed_rail'
                reason = '高铁舒适便捷，准点率高'
            else:
                recommended = 'airplane'
                reason = '飞机速度快，适合时间有限的旅客'
            
            return {
                'budget': budget,
                'intercity_options': transport_options,
                'local_transport': local_transport,
                'recommendation': {
                    'preferred': recommended,
                    'reason': reason,
                    'estimated_total_cost': transport_options[recommended]['estimated_cost'] + local_budget
                },
                'general_tips': [
                    '提前比较各种交通方式的价格和时间',
                    '考虑旅行保险覆盖交通延误',
                    '保留所有交通票据以备报销',
                    '下载相关交通APP获取实时信息'
                ]
            }
            
        except Exception as e:
            logger.error(f"Error planning transportation: {str(e)}")
            return {
                'budget': budget,
                'error': str(e),
                'intercity_options': {},
                'local_transport': {}
            }
    
    def _add_custom_features(self, preferences: Dict[str, Any]) -> List[str]:
        """Add custom features based on user preferences."""
        features = []
        
        if preferences.get('photography'):
            features.append('Photography spots and golden hour recommendations')
        
        if preferences.get('adventure'):
            features.append('Adventure activities and outdoor experiences')
        
        if preferences.get('culture'):
            features.append('Deep cultural immersion experiences')
        
        if preferences.get('relaxation'):
            features.append('Spa and wellness activities')
        
        if preferences.get('nightlife'):
            features.append('Nightlife and entertainment recommendations')
        
        return features if features else ['Balanced mix of activities and experiences']
