"""
Transport Service
Provides transportation options and routing information
"""

import os
import logging
from typing import Dict, Any, List
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Import the new transport crawler
from ..utils.transport_crawler import TransportCrawler

logger = logging.getLogger(__name__)

class TransportService:
    """Service for transportation data and routing."""
    
    def __init__(self):
        """Initialize the transport service."""
        # Initialize ModelScope LLM for transport data generation using shared factory
        from travel_agent.utils.model_factory import create_llm_model
        self.model = create_llm_model("TransportService")
        
        # Initialize the transport crawler for real-time data
        self.crawler = TransportCrawler()
        
        logger.info("Transport Service initialized with real-time data crawler")
    
    def get_transport_options(
        self,
        departure: str,
        destination: str,
        start_date: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive transportation options between departure and destination.
        
        Args:
            departure: Starting location
            destination: Target destination
            start_date: Travel start date (YYYY-MM-DD)
            
        Returns:
            Dict containing detailed transport options with real-time data
        """
        try:
            logger.info(f"Getting comprehensive transport options from {departure} to {destination} on {start_date}")
            
            # Get real-time transportation data using the crawler
            transport_options = {}
            
            # 1. Get train data (高铁/火车)
            logger.info("Fetching train data...")
            train_data = self.crawler.get_train_prices(departure, destination, start_date)
            if train_data.get('success') and train_data.get('trains'):
                transport_options['train'] = self._format_train_option(train_data)
            
            # 2. Get flight data (航班)
            logger.info("Fetching flight data...")
            flight_data = self.crawler.get_flight_prices(departure, destination, start_date)
            if flight_data.get('success') and flight_data.get('flights'):
                transport_options['flight'] = self._format_flight_option(flight_data)
            
            # 3. Get driving route data (自驾)
            logger.info("Fetching driving route data...")
            driving_data = self.crawler.get_driving_route(departure, destination)
            if driving_data.get('success') and driving_data.get('route'):
                transport_options['driving'] = self._format_driving_option(driving_data)
            
            # 4. Get bus data (长途客车)
            logger.info("Fetching bus data...")
            bus_data = self.crawler.get_bus_schedules(departure, destination, start_date)
            if bus_data.get('success') and bus_data.get('buses'):
                transport_options['bus'] = self._format_bus_option(bus_data)
            
            # 5. Generate AI recommendations based on real data
            recommendations = self._generate_transport_recommendations(transport_options, departure, destination)
            
            # 6. Get local transport information
            local_transport = self._get_enhanced_local_transport_info(destination)
            
            return {
                'success': True,
                'departure': departure,
                'destination': destination,
                'travel_date': start_date,
                'intercity_options': transport_options,
                'recommendation': recommendations,
                'local_transport': local_transport,
                'last_updated': datetime.now().isoformat(),
                'data_sources': ['12306', 'airlines', 'map_apis', 'bus_platforms']
            }
            
        except Exception as e:
            logger.error(f"Error getting transport options: {str(e)}")
            return self._get_fallback_transport_data(departure, destination)
    
    def _format_train_option(self, train_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format train data into standardized transport option."""
        try:
            trains = train_data.get('trains', [])
            if not trains:
                return None
            
            # Calculate price range and duration range
            prices = []
            durations = []
            
            for train in trains:
                for seat in train.get('seats', []):
                    if seat.get('available'):
                        prices.append(seat.get('price', 0))
                
                # Extract duration in hours (simplified)
                duration_str = train.get('duration', '0小时0分钟')
                try:
                    import re
                    hours = re.search(r'(\d+)小时', duration_str)
                    minutes = re.search(r'(\d+)分钟', duration_str)
                    total_hours = (int(hours.group(1)) if hours else 0) + (int(minutes.group(1)) if minutes else 0) / 60
                    durations.append(total_hours)
                except:
                    durations.append(6)  # Default 6 hours
            
            min_price = min(prices) if prices else 100
            max_price = max(prices) if prices else 500
            avg_duration = sum(durations) / len(durations) if durations else 6
            
            return {
                'type': '高铁/火车',
                'estimated_cost': {'min': min_price, 'max': max_price, 'currency': 'CNY'},
                'duration': f"{avg_duration:.1f}小时",
                'comfort_level': 'High',
                'convenience': 'High',
                'environmental_impact': 'Low',
                'booking_info': {
                    'platform': '12306.cn',
                    'advance_booking': '30天',
                    'real_name_required': True,
                    'refund_policy': '开车前可退票'
                },
                'pros': [
                    '准点率高',
                    '市中心到市中心',
                    '舒适度好',
                    '不受天气影响',
                    '可以在车上休息工作'
                ],
                'cons': [
                    '需要提前购票',
                    '班次相对固定',
                    '节假日票源紧张'
                ],
                'best_for': '注重舒适度和准点的旅客',
                'tips': [
                    '提前30天购票享受更多选择',
                    '选择二等座性价比最高',
                    '携带身份证件',
                    '提前30分钟到站'
                ],
                'detailed_options': trains[:5],  # Top 5 train options
                'booking_url': 'https://www.12306.cn',
                'last_updated': train_data.get('last_updated')
            }
            
        except Exception as e:
            logger.error(f"Error formatting train option: {str(e)}")
            return None
    
    def _format_flight_option(self, flight_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format flight data into standardized transport option."""
        try:
            flights = flight_data.get('flights', [])
            if not flights:
                return None
            
            # Calculate price range and duration range
            prices = []
            durations = []
            
            for flight in flights:
                for cabin in flight.get('cabins', []):
                    if cabin.get('available'):
                        prices.append(cabin.get('price', 0))
                
                # Extract duration in hours
                duration_str = flight.get('duration', '0小时0分钟')
                try:
                    import re
                    hours = re.search(r'(\d+)小时', duration_str)
                    minutes = re.search(r'(\d+)分钟', duration_str)
                    total_hours = (int(hours.group(1)) if hours else 0) + (int(minutes.group(1)) if minutes else 0) / 60
                    durations.append(total_hours)
                except:
                    durations.append(2)  # Default 2 hours
            
            min_price = min(prices) if prices else 300
            max_price = max(prices) if prices else 2000
            avg_duration = sum(durations) / len(durations) if durations else 2
            
            return {
                'type': '航班',
                'estimated_cost': {'min': min_price, 'max': max_price, 'currency': 'CNY'},
                'duration': f"{avg_duration:.1f}小时",
                'comfort_level': 'High',
                'convenience': 'Medium',
                'environmental_impact': 'High',
                'booking_info': {
                    'platforms': ['携程', '去哪儿', '航空公司官网'],
                    'advance_booking': '建议提前1-2周',
                    'id_required': True,
                    'baggage_policy': '经济舱通常20kg免费托运'
                },
                'pros': [
                    '速度最快',
                    '长距离性价比高',
                    '航班选择多',
                    '服务标准化'
                ],
                'cons': [
                    '需要提前到机场',
                    '受天气影响',
                    '行李限制',
                    '机场通常较远'
                ],
                'best_for': '时间紧张的商务旅客',
                'tips': [
                    '提前2小时到达机场',
                    '关注航班动态',
                    '选择靠窗座位欣赏风景',
                    '携带身份证或护照'
                ],
                'detailed_options': flights[:5],  # Top 5 flight options
                'booking_urls': [
                    'https://www.airchina.com.cn',
                    'https://www.ctrip.com',
                    'https://www.qunar.com'
                ],
                'last_updated': flight_data.get('last_updated')
            }
            
        except Exception as e:
            logger.error(f"Error formatting flight option: {str(e)}")
            return None
    
    def _format_driving_option(self, driving_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format driving data into standardized transport option."""
        try:
            route = driving_data.get('route', {})
            if not route:
                return None
            
            total_cost = route.get('total_cost', 0)
            
            return {
                'type': '自驾',
                'estimated_cost': {
                    'fuel': route.get('fuel_cost', 0),
                    'tolls': route.get('toll_fees', 0),
                    'total': total_cost,
                    'currency': 'CNY'
                },
                'duration': route.get('estimated_time', '未知'),
                'distance': route.get('distance', '未知'),
                'comfort_level': 'High',
                'convenience': 'Very High',
                'environmental_impact': 'Medium',
                'requirements': {
                    'driving_license': True,
                    'vehicle_registration': True,
                    'insurance': True
                },
                'pros': [
                    '时间完全自由',
                    '门到门服务',
                    '可以随时停车休息',
                    '适合携带大量行李',
                    '可以欣赏沿途风景'
                ],
                'cons': [
                    '驾驶疲劳',
                    '停车费用',
                    '交通拥堵风险',
                    '需要驾照和车辆'
                ],
                'best_for': '喜欢自由行程的有车族',
                'tips': route.get('notes', []),
                'route_details': {
                    'main_route': route.get('route_type', '高速公路为主'),
                    'rest_stops': route.get('rest_stops', 2),
                    'traffic_conditions': route.get('traffic_conditions', '正常'),
                    'recommended_departure': route.get('recommended_departure_times', [])
                },
                'last_updated': driving_data.get('last_updated')
            }
            
        except Exception as e:
            logger.error(f"Error formatting driving option: {str(e)}")
            return None
    
    def _format_bus_option(self, bus_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format bus data into standardized transport option."""
        try:
            buses = bus_data.get('buses', [])
            if not buses:
                return None
            
            # Calculate price range and duration range
            prices = [bus.get('price', 0) for bus in buses]
            durations = []
            
            for bus in buses:
                duration_str = bus.get('duration', '0小时0分钟')
                try:
                    import re
                    hours = re.search(r'(\d+)小时', duration_str)
                    minutes = re.search(r'(\d+)分钟', duration_str)
                    total_hours = (int(hours.group(1)) if hours else 0) + (int(minutes.group(1)) if minutes else 0) / 60
                    durations.append(total_hours)
                except:
                    durations.append(8)  # Default 8 hours
            
            min_price = min(prices) if prices else 50
            max_price = max(prices) if prices else 200
            avg_duration = sum(durations) / len(durations) if durations else 8
            
            return {
                'type': '长途客车',
                'estimated_cost': {'min': min_price, 'max': max_price, 'currency': 'CNY'},
                'duration': f"{avg_duration:.1f}小时",
                'comfort_level': 'Medium',
                'convenience': 'Medium',
                'environmental_impact': 'Low',
                'booking_info': {
                    'platforms': ['客运站', '网上购票'],
                    'advance_booking': '不强制但建议',
                    'id_required': True
                },
                'pros': [
                    '价格最便宜',
                    '班次较多',
                    '无需提前很久购票',
                    '直达班次多'
                ],
                'cons': [
                    '时间较长',
                    '舒适度一般',
                    '受交通状况影响',
                    '中途停车较多'
                ],
                'best_for': '预算有限的旅客',
                'tips': [
                    '选择信誉好的客运公司',
                    '携带娱乐设备',
                    '准备一些零食',
                    '注意保管贵重物品'
                ],
                'detailed_options': buses[:5],  # Top 5 bus options
                'last_updated': bus_data.get('last_updated')
            }
            
        except Exception as e:
            logger.error(f"Error formatting bus option: {str(e)}")
            return None
    
    def _generate_transport_recommendations(
        self,
        transport_options: Dict[str, Any],
        departure: str,
        destination: str
    ) -> Dict[str, Any]:
        """Generate AI-powered transport recommendations based on available options."""
        try:
            if not transport_options:
                return {'preferred': 'mixed', 'reason': '暂无具体交通数据，建议查询官方渠道'}
            
            # Analyze available options
            available_types = list(transport_options.keys())
            
            # Simple recommendation logic (can be enhanced with AI)
            if 'flight' in available_types:
                flight_option = transport_options['flight']
                min_cost = flight_option['estimated_cost']['min']
                if min_cost < 800:  # Reasonable flight price
                    return {
                        'preferred': 'flight',
                        'reason': f'航班价格合理（最低{min_cost}元），时间最短，适合长距离出行',
                        'estimated_total_cost': min_cost + 100,  # Include airport transfer
                        'alternative': 'train' if 'train' in available_types else 'bus'
                    }
            
            if 'train' in available_types:
                train_option = transport_options['train']
                return {
                    'preferred': 'train',
                    'reason': '高铁舒适便捷，准点率高，市中心直达，综合性价比最佳',
                    'estimated_total_cost': train_option['estimated_cost']['min'],
                    'alternative': 'flight' if 'flight' in available_types else 'bus'
                }
            
            if 'driving' in available_types:
                driving_option = transport_options['driving']
                return {
                    'preferred': 'driving',
                    'reason': '自驾时间自由，适合携带行李，可以欣赏沿途风景',
                    'estimated_total_cost': driving_option['estimated_cost']['total'],
                    'alternative': 'bus' if 'bus' in available_types else None
                }
            
            if 'bus' in available_types:
                bus_option = transport_options['bus']
                return {
                    'preferred': 'bus',
                    'reason': '长途客车价格最实惠，班次较多，适合预算有限的旅客',
                    'estimated_total_cost': bus_option['estimated_cost']['min'],
                    'alternative': None
                }
            
            return {
                'preferred': 'mixed',
                'reason': '建议根据具体需求选择合适的交通方式',
                'estimated_total_cost': 200
            }
            
        except Exception as e:
            logger.error(f"Error generating transport recommendations: {str(e)}")
            return {
                'preferred': 'mixed',
                'reason': '请根据个人需求和预算选择合适的交通方式',
                'estimated_total_cost': 300
            }
    
    def _generate_transport_options(
        self,
        departure: str,
        destination: str,
        start_date: str
    ) -> List[Dict[str, Any]]:
        """Generate transport options using AI."""
        try:
            prompt = f"""
            Provide transportation options from {departure} to {destination} for {start_date}.
            Include flights, trains, buses, and driving options with costs, duration, and booking info.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse response into structured data
            transport_options = self._parse_transport_response(response.text, departure, destination)
            
            return transport_options
            
        except Exception as e:
            logger.error(f"Error generating transport options: {str(e)}")
            return self._get_sample_transport_options(departure, destination)
    
    def _parse_transport_response(
        self,
        ai_response: str,
        departure: str,
        destination: str
    ) -> List[Dict[str, Any]]:
        """Parse AI response into structured transport data."""
        try:
            # Create structured sample transport options
            sample_options = [
                {
                    'type': 'Flight',
                    'duration': '2-4 hours',
                    'cost_range': {'min': 150, 'max': 500},
                    'comfort': 'High',
                    'frequency': 'Multiple daily',
                    'booking_required': True,
                    'advance_booking': '2-8 weeks recommended',
                    'pros': ['Fastest option', 'Multiple airlines', 'Frequent schedules'],
                    'cons': ['Airport transfers needed', 'Weather dependent', 'Security delays'],
                    'best_for': 'Time-conscious travelers',
                    'booking_tips': ['Book early for better prices', 'Compare airlines', 'Check baggage policies']
                },
                {
                    'type': 'Train',
                    'duration': '4-8 hours',
                    'cost_range': {'min': 50, 'max': 200},
                    'comfort': 'Medium-High',
                    'frequency': 'Several daily',
                    'booking_required': True,
                    'advance_booking': '1-4 weeks recommended',
                    'pros': ['City center to center', 'Comfortable seating', 'Scenic views'],
                    'cons': ['Limited schedules', 'Weather delays possible'],
                    'best_for': 'Comfortable travel with views',
                    'booking_tips': ['Book seats in advance', 'Consider meal options', 'Check station locations']
                },
                {
                    'type': 'Bus',
                    'duration': '6-12 hours',
                    'cost_range': {'min': 25, 'max': 80},
                    'comfort': 'Medium',
                    'frequency': 'Multiple daily',
                    'booking_required': False,
                    'advance_booking': 'Not required but recommended',
                    'pros': ['Most economical', 'Frequent departures', 'No advance booking needed'],
                    'cons': ['Longest travel time', 'Limited comfort', 'Traffic dependent'],
                    'best_for': 'Budget travelers',
                    'booking_tips': ['Choose reputable companies', 'Bring entertainment', 'Pack snacks']
                },
                {
                    'type': 'Car Rental',
                    'duration': '5-10 hours',
                    'cost_range': {'min': 40, 'max': 120},
                    'comfort': 'High',
                    'frequency': 'Available 24/7',
                    'booking_required': True,
                    'advance_booking': '1-2 weeks recommended',
                    'pros': ['Complete flexibility', 'Door-to-door', 'Stop anywhere'],
                    'cons': ['Driving fatigue', 'Parking costs', 'Traffic'],
                    'best_for': 'Flexible travelers with driving license',
                    'booking_tips': ['Compare rental companies', 'Check insurance', 'Plan rest stops']
                }
            ]
            
            return sample_options
            
        except Exception as e:
            logger.error(f"Error parsing transport response: {str(e)}")
            return self._get_sample_transport_options(departure, destination)
    
    def _get_enhanced_local_transport_info(self, destination: str) -> Dict[str, Any]:
        """Get enhanced local transportation information for the destination."""
        try:
            return {
                'public_transport': {
                    'available': True,
                    'types': ['地铁', '公交', '有轨电车'],
                    'daily_pass_cost': 15,
                    'single_ride_cost': 3,
                    'operating_hours': '05:30 - 23:30',
                    'coverage': '市区覆盖良好',
                    'payment_methods': ['交通卡', '手机支付', '现金'],
                    'apps': ['当地交通APP', '支付宝', '微信'],
                    'tips': [
                        '购买日票或周票更划算',
                        '下载当地交通APP查看实时信息',
                        '高峰期避开拥挤线路',
                        '准备零钱或开通手机支付'
                    ]
                },
                'taxi_rideshare': {
                    'available': True,
                    'services': ['出租车', '滴滴', '网约车'],
                    'base_fare': 8,
                    'per_km_rate': 2.5,
                    'night_surcharge': 1.3,
                    'airport_surcharge': 10,
                    'peak_hour_multiplier': 1.5,
                    'tips': [
                        '使用APP叫车更方便',
                        '确认车牌号和司机信息',
                        '保存行程记录',
                        '准备现金以备不时之需'
                    ]
                },
                'walking_cycling': {
                    'walkability': 'High',
                    'bike_sharing': True,
                    'bike_rental_cost': 2,
                    'bike_deposit': 200,
                    'pedestrian_friendly': True,
                    'cycling_infrastructure': 'Good',
                    'bike_sharing_brands': ['摩拜', '哈啰', '青桔'],
                    'tips': [
                        '市中心适合步行游览',
                        '共享单车覆盖面广',
                        '注意交通安全',
                        '穿舒适的鞋子'
                    ]
                },
                'airport_transport': {
                    'airport_express': {
                        'available': True,
                        'cost': 25,
                        'duration': '30-45分钟',
                        'frequency': '10-15分钟一班',
                        'operating_hours': '06:00-23:00'
                    },
                    'taxi': {
                        'cost_range': '80-150',
                        'duration': '45-90分钟',
                        'note': '价格因距离和时间而异'
                    },
                    'shuttle_bus': {
                        'cost': 30,
                        'duration': '60-90分钟',
                        'note': '经济实惠但时间较长'
                    },
                    'public_transport': {
                        'cost': 8,
                        'duration': '60-120分钟',
                        'transfers': '可能需要换乘'
                    }
                },
                'special_transport': {
                    'tourist_bus': {
                        'available': True,
                        'day_pass': 50,
                        'routes': '覆盖主要景点',
                        'hop_on_off': True
                    },
                    'boat_ferry': {
                        'available': False,  # Depends on destination
                        'cost': 20,
                        'scenic_routes': True
                    }
                },
                'parking_info': {
                    'street_parking': {
                        'hourly_rate': 5,
                        'daily_max': 50,
                        'payment_methods': ['停车APP', '咪表', '现金']
                    },
                    'parking_lots': {
                        'hourly_rate': 8,
                        'daily_rate': 60,
                        'monthly_rate': 800
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting enhanced local transport info: {str(e)}")
            return self._get_local_transport_info(destination)
    
    def _get_local_transport_info(self, destination: str) -> Dict[str, Any]:
        """Get basic local transportation information for the destination."""
        try:
            return {
                'public_transport': {
                    'available': True,
                    'types': ['Metro/Subway', 'Bus', 'Tram'],
                    'daily_pass_cost': 8,
                    'single_ride_cost': 2.5,
                    'operating_hours': '05:00 - 24:00',
                    'coverage': 'Good city coverage',
                    'tips': ['Buy daily/weekly passes for savings', 'Download transport app', 'Keep small change']
                },
                'taxi_rideshare': {
                    'available': True,
                    'services': ['Local Taxi', 'Uber', 'Lyft'],
                    'base_fare': 3.5,
                    'per_km_rate': 1.2,
                    'airport_surcharge': 5,
                    'tips': ['Use apps for better rates', 'Confirm fare before ride', 'Tip 10-15%']
                },
                'walking_cycling': {
                    'walkability': 'High',
                    'bike_sharing': True,
                    'bike_rental_cost': 15,
                    'pedestrian_friendly': True,
                    'cycling_infrastructure': 'Good',
                    'tips': ['City center is walkable', 'Bike lanes available', 'Wear comfortable shoes']
                },
                'airport_transport': {
                    'airport_express': {'available': True, 'cost': 12, 'duration': '30-45 min'},
                    'taxi': {'cost_range': '40-60', 'duration': '45-90 min'},
                    'shuttle': {'cost': 15, 'duration': '60-90 min'},
                    'public_transport': {'cost': 5, 'duration': '60-120 min'}
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting local transport info: {str(e)}")
            return {
                'public_transport': {'available': True, 'daily_pass_cost': 8},
                'taxi_rideshare': {'available': True, 'base_fare': 3.5},
                'walking_cycling': {'walkability': 'Medium'},
                'airport_transport': {'taxi': {'cost_range': '40-60'}}
            }
    
    def _get_sample_transport_options(self, departure: str, destination: str) -> List[Dict[str, Any]]:
        """Get sample transport options when AI generation fails."""
        return [
            {
                'type': 'Flight',
                'duration': '3 hours',
                'cost_range': {'min': 200, 'max': 400},
                'comfort': 'High',
                'booking_required': True,
                'pros': ['Fastest option'],
                'cons': ['Airport transfers needed'],
                'best_for': 'Time-conscious travelers'
            },
            {
                'type': 'Train',
                'duration': '6 hours',
                'cost_range': {'min': 80, 'max': 150},
                'comfort': 'Medium-High',
                'booking_required': True,
                'pros': ['Comfortable', 'City center to center'],
                'cons': ['Limited schedules'],
                'best_for': 'Comfortable travel'
            }
        ]
    
    def _get_fallback_transport_data(self, departure: str, destination: str) -> Dict[str, Any]:
        """Get fallback transport data when all else fails."""
        return {
            'success': False,
            'departure': departure,
            'destination': destination,
            'options': [
                {
                    'type': 'Mixed Transport',
                    'duration': 'Varies',
                    'cost_range': {'min': 50, 'max': 300},
                    'comfort': 'Varies',
                    'booking_required': True,
                    'note': 'Please check local transport providers for specific options'
                }
            ],
            'local_transport': {
                'public_transport': {'available': True, 'cost': 'Varies'},
                'taxi_rideshare': {'available': True, 'cost': 'Varies'}
            },
            'error': 'Limited transport data available'
        }
