"""
Report Generator Agent
Responsible for generating beautiful HTML travel reports
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader, Template
import google.generativeai as genai
from dotenv import load_dotenv

# Add the parent directory to sys.path to enable absolute imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from travel_agent.utils.markdown_converter import MarkdownConverter

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

logger = logging.getLogger(__name__)

class ReportGeneratorAgent:
    """Agent responsible for generating HTML travel reports."""
    
    def __init__(self):
        """Initialize the report generator."""
        # Initialize Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
        
        # Initialize Gemini for content enhancement
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        logger.info("Report Generator Agent initialized")
    
    def generate_html_report(
        self,
        travel_data: Dict[str, Any],
        travel_plans: List[Dict[str, Any]],
        destination: str,
        start_date: str,
        duration: int,
        budget: float
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive HTML travel report.
        
        Args:
            travel_data: Collected travel data
            travel_plans: Generated travel plans
            destination: Destination name
            start_date: Travel start date
            duration: Trip duration
            budget: Total budget
            
        Returns:
            Dict containing generation result and file path
        """
        try:
            logger.info(f"Generating HTML report for {destination}")
            
            # Prepare report data
            report_data = self._prepare_report_data(
                travel_data, travel_plans, destination, start_date, duration, budget
            )
            
            # Generate enhanced content using AI
            enhanced_data = self._enhance_report_content(report_data)
            
            # Render HTML template
            html_content = self._render_html_template(enhanced_data)
            
            # Save to file
            file_path = self._save_html_report(html_content, destination, start_date)
            
            return {
                'success': True,
                'file_path': file_path,
                'message': f'HTML report generated successfully: {file_path}'
            }
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'file_path': None
            }
    
    def _prepare_report_data(
        self,
        travel_data: Dict[str, Any],
        travel_plans: List[Dict[str, Any]],
        destination: str,
        start_date: str,
        duration: int,
        budget: float
    ) -> Dict[str, Any]:
        """Prepare structured data for the HTML report."""
        try:
            logger.info(f"Preparing report data for {destination}")
            logger.info(f"Input parameters: destination={destination}, start_date={start_date}, duration={duration}, budget={budget}")
            logger.info(f"Travel data keys: {list(travel_data.keys()) if travel_data else 'None'}")
            logger.info(f"Travel plans count: {len(travel_plans) if travel_plans else 0}")
            
            # Validate input parameters - CRITICAL FIX
            if not destination or destination.strip() == '':
                destination = '未知目的地'
                logger.warning("Empty destination provided, using fallback")
            
            if not start_date or start_date.strip() == '':
                start_date = datetime.now().strftime('%Y-%m-%d')
                logger.warning("Empty start_date provided, using current date")
            
            if not duration or duration <= 0:
                duration = 7
                logger.warning("Invalid duration provided, using 7 days")
            
            if not budget or budget <= 0:
                budget = 5000.0
                logger.warning("Invalid budget provided, using 5000")
            
            # Extract key information with detailed logging and validation
            destination_info = travel_data.get('destination_info', {}) if travel_data else {}
            logger.info(f"Destination info: {destination_info.get('name', 'No name')} - {len(str(destination_info.get('description', '')))}")
            
            weather_data = travel_data.get('weather_data', {}) if travel_data else {}
            logger.info(f"Weather data success: {weather_data.get('success', False)}")
            
            attractions = travel_data.get('attractions', []) if travel_data else []
            logger.info(f"Attractions count: {len(attractions)}")
            
            accommodations = travel_data.get('accommodations', []) if travel_data else []
            logger.info(f"Accommodations count: {len(accommodations)}")
            
            dining = travel_data.get('dining', []) if travel_data else []
            logger.info(f"Dining options count: {len(dining)}")
            
            transportation = travel_data.get('transportation', {}) if travel_data else {}
            logger.info(f"Transportation data keys: {list(transportation.keys()) if transportation else 'None'}")
            
            local_info = travel_data.get('local_info', {}) if travel_data else {}
            ai_insights = travel_data.get('ai_insights', {}) if travel_data else {}
            
            # Process weather data - ensure we always have weather information to display
            weather_forecast = weather_data.get('forecast', [])
            weather_info = {
                'forecast': weather_forecast,
                'source': weather_data.get('source', 'Unknown'),
                'success': weather_data.get('success', False),
                'error': weather_data.get('error', ''),
                'note': weather_data.get('note', ''),
                'current_weather': weather_data.get('current_weather', {})
            }
            
            # CRITICAL FIX: Ensure we have valid travel plans
            if not travel_plans or len(travel_plans) == 0:
                logger.warning("No travel plans provided, creating default plans")
                travel_plans = self._create_default_travel_plans(budget, duration)
                logger.info(f"Created {len(travel_plans)} default travel plans")
            
            # Validate travel plans structure
            validated_plans = []
            for plan in travel_plans:
                if isinstance(plan, dict) and plan.get('plan_type'):
                    validated_plans.append(plan)
                else:
                    logger.warning(f"Invalid plan structure: {plan}")
            
            if not validated_plans:
                logger.error("No valid travel plans after validation, creating emergency fallback")
                validated_plans = self._create_emergency_fallback_plans(budget, duration)
            
            travel_plans = validated_plans
            
            report_data = {
                # Header Information - CRITICAL: These must match the input parameters exactly
                'title': f'{destination}旅行计划',
                'destination': destination,  # Use the validated input parameter
                'start_date': start_date,    # Use the validated input parameter
                'duration': duration,        # Use the validated input parameter
                'budget': budget,           # Use the validated input parameter
                'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                
                # Destination Overview
                'destination_info': destination_info,
                'weather_forecast': weather_forecast,
                'weather_info': weather_info,
                
                # Travel Plans - CRITICAL: Ensure we have plans
                'travel_plans': travel_plans,
                'plans_count': len(travel_plans),
                
                # Transportation
                'transportation_options': transportation.get('intercity_options', {}),
                'transportation_recommendation': transportation.get('recommendation', {}),
                'local_transport': transportation.get('local_transport', {}),
                
                # Attractions & Activities
                'attractions': attractions[:10] if attractions else [],  # Top 10 attractions
                'attractions_count': len(attractions),
                
                # Accommodations
                'accommodations': accommodations[:5] if accommodations else [],  # Top 5 accommodations
                
                # Dining
                'dining_options': dining[:8] if dining else [],  # Top 8 dining options
                
                # Local Information
                'local_info': local_info,
                'practical_tips': local_info.get('practical_tips', ''),
                'useful_phrases': local_info.get('useful_phrases', []),
                'emergency_numbers': local_info.get('emergency_numbers', []),
                
                # AI Insights
                'ai_insights': ai_insights.get('recommendations', ''),
                
                # Budget Summary
                'budget_summary': self._create_budget_summary(travel_plans, budget),
                
                # Additional metadata
                'meta': {
                    'generated_by': 'Travel AI Agent',
                    'version': '1.0',
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            # Log the final report data structure for debugging
            logger.info(f"Final report data prepared:")
            logger.info(f"  - Title: {report_data['title']}")
            logger.info(f"  - Destination: {report_data['destination']}")
            logger.info(f"  - Start date: {report_data['start_date']}")
            logger.info(f"  - Duration: {report_data['duration']}")
            logger.info(f"  - Budget: {report_data['budget']}")
            logger.info(f"  - Plans count: {report_data['plans_count']}")
            logger.info(f"  - Generation date: {report_data['generation_date']}")
            
            # CRITICAL: Validate that all required fields are present and not empty
            required_fields = ['title', 'destination', 'start_date', 'duration', 'budget', 'travel_plans']
            for field in required_fields:
                if field not in report_data or report_data[field] is None:
                    logger.error(f"Missing required field: {field}")
                    raise ValueError(f"Missing required field: {field}")
                if field == 'travel_plans' and len(report_data[field]) == 0:
                    logger.error("No travel plans in final report data")
                    raise ValueError("No travel plans in final report data")
            
            return report_data
            
        except Exception as e:
            logger.error(f"Error preparing report data: {str(e)}", exc_info=True)
            # Return a minimal but VALID report data structure with emergency fallback
            emergency_plans = self._create_emergency_fallback_plans(budget if budget and budget > 0 else 5000, duration if duration and duration > 0 else 7)
            return {
                'title': f'{destination if destination else "旅行目的地"}旅行计划',
                'destination': destination if destination else '旅行目的地',
                'start_date': start_date if start_date else datetime.now().strftime('%Y-%m-%d'),
                'duration': duration if duration and duration > 0 else 7,
                'budget': budget if budget and budget > 0 else 5000,
                'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'travel_plans': emergency_plans,
                'plans_count': len(emergency_plans),
                'weather_forecast': [],
                'weather_info': {'success': False, 'error': '天气数据获取失败'},
                'attractions': [],
                'accommodations': [],
                'dining_options': [],
                'local_info': {},
                'ai_insights': '由于数据收集过程中出现问题，这是一个基础的旅行计划。建议您在出行前进一步研究目的地信息。',
                'error': str(e)
            }
    
    def _enhance_report_content(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to enhance report content with additional insights."""
        try:
            destination = report_data.get('destination', '未知目的地')
            duration = report_data.get('duration', 7)
            budget = report_data.get('budget', 5000)
            
            # Generate additional content sections in Chinese
            prompt = f"""
            请为{destination}的{duration}天旅行计划（预算{budget}元）创建详细的中文旅行指南内容。

            请生成以下内容，全部使用中文：

            1. 目的地介绍（2-3段，介绍{destination}的历史、文化、特色和魅力）
            2. 有趣的事实（5个关于{destination}的有趣知识点）
            3. 摄影技巧（5个针对{destination}的摄影建议）
            4. 文化礼仪（5个在{destination}需要注意的文化礼仪）
            5. 打包建议（根据{destination}的气候和季节特点）
            6. 应急准备（在{destination}旅行的安全建议）
            7. 省钱技巧（在{destination}旅行的省钱方法）
            8. 个性化推荐（基于{duration}天行程和{budget}元预算的详细建议，包括隐藏景点、当地体验、美食推荐等）

            请确保所有内容都是中文，实用且具体。
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse and add enhanced content
            enhanced_content = self._parse_enhanced_content(response.text, destination)
            report_data.update(enhanced_content)
            
            return report_data
            
        except Exception as e:
            logger.warning(f"Error enhancing report content: {str(e)}")
            # Return default Chinese content
            return self._get_default_chinese_content(report_data)
    
    def _parse_enhanced_content(self, ai_response: str, destination: str = '') -> Dict[str, Any]:
        """Parse AI-generated enhanced content."""
        try:
            # If we have a good AI response, use it directly for the insights
            if ai_response and len(ai_response) > 200:
                # Convert Markdown to HTML for AI insights
                formatted_ai_insights = MarkdownConverter.convert(ai_response)
                
                enhanced_content = {
                    'destination_introduction': f'欢迎来到{destination}！这里是一个充满魅力的旅行目的地，拥有丰富的历史文化、独特的自然风光和令人难忘的旅行体验。无论您是历史爱好者、美食探索者还是自然风光的追求者，{destination}都能为您提供精彩纷呈的旅行回忆。',
                    'did_you_know_facts': [
                        f'{destination}拥有深厚的历史文化底蕴',
                        f'{destination}的传统美食独具特色',
                        f'{destination}的建筑风格体现了当地文化',
                        f'{destination}有许多值得探索的隐藏景点',
                        f'{destination}的自然风光四季各有特色'
                    ],
                    'photography_tips': [
                        '选择黄金时段拍摄，光线更加柔和迷人',
                        '捕捉当地人的日常生活瞬间',
                        '利用建筑和自然景观创造层次感',
                        '尝试不同的拍摄角度和构图',
                        '尊重当地的拍摄规定和文化习俗'
                    ],
                    'cultural_etiquette': [
                        '尊重当地的传统习俗和文化',
                        '在宗教场所保持庄重得体',
                        '学习基本的当地语言问候语',
                        '了解当地的用餐礼仪和习惯',
                        '以友善和尊重的态度与当地人交流'
                    ],
                    'ai_insights': formatted_ai_insights  # Use formatted HTML for insights
                }
            else:
                # Fallback to default content
                enhanced_content = self._get_default_chinese_content({'destination': destination})
            
            return enhanced_content
            
        except Exception as e:
            logger.warning(f"Error parsing enhanced content: {str(e)}")
            return self._get_default_chinese_content({'destination': destination})
    
    def _get_default_chinese_content(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get default Chinese content when AI generation fails."""
        destination = report_data.get('destination', '目的地')
        
        return {
            'destination_introduction': f'欢迎来到{destination}！这里是一个充满魅力的旅行目的地，拥有丰富的历史文化、独特的自然风光和令人难忘的旅行体验。无论您是历史爱好者、美食探索者还是自然风光的追求者，{destination}都能为您提供精彩纷呈的旅行回忆。在这里，您可以深入了解当地的传统文化，品尝地道的美食，欣赏壮丽的自然景观，感受当地人民的热情好客。',
            'did_you_know_facts': [
                f'{destination}拥有深厚的历史文化底蕴，见证了数百年的历史变迁',
                f'{destination}的传统美食独具特色，融合了多种烹饪技艺',
                f'{destination}的建筑风格体现了当地独特的文化特色',
                f'{destination}有许多值得探索的隐藏景点和当地秘境',
                f'{destination}的自然风光四季各有特色，每个季节都有不同的美景'
            ],
            'photography_tips': [
                '选择黄金时段（日出日落）拍摄，光线更加柔和迷人',
                '捕捉当地人的日常生活瞬间，展现真实的文化氛围',
                '利用建筑和自然景观创造层次感和纵深感',
                '尝试不同的拍摄角度和构图方式，发现独特视角',
                '尊重当地的拍摄规定和文化习俗，避免敏感区域'
            ],
            'cultural_etiquette': [
                '尊重当地的传统习俗和文化传统',
                '在宗教场所保持庄重得体的行为举止',
                '学习基本的当地语言问候语，展现友好态度',
                '了解当地的用餐礼仪和社交习惯',
                '以友善和尊重的态度与当地人交流互动'
            ],
            'ai_insights': f'基于您的{destination}旅行计划，我们为您精心准备了个性化的旅行建议。建议您提前了解当地的文化背景和历史，这将让您的旅行体验更加丰富。在行程安排上，建议将热门景点和小众景点相结合，既能欣赏到经典美景，又能发现独特的当地体验。美食方面，不要错过当地的特色菜肴和街头小食，这些往往是最能体现当地文化的美味。住宿选择上，可以考虑具有当地特色的民宿或精品酒店，获得更加authentic的体验。交通方面，建议使用当地的公共交通工具，既经济实惠又能更好地融入当地生活。最后，保持开放的心态，与当地人交流，您会发现许多意想不到的精彩体验。'
        }
    
    def _create_default_travel_plans(self, budget: float, duration: int) -> List[Dict[str, Any]]:
        """Create default travel plans when none are provided."""
        try:
            logger.info(f"Creating default travel plans for budget {budget} and duration {duration}")
            
            # Create two basic plans: Economic and Comfort
            economic_budget = budget * 0.8
            comfort_budget = budget
            
            plans = [
                {
                    'plan_type': 'Economic',
                    'description': 'Budget-friendly travel plan focusing on value and essential experiences',
                    'total_budget': economic_budget,
                    'budget_allocation': {
                        'transportation': {'amount': economic_budget * 0.32, 'percentage': 32},
                        'accommodation': {'amount': economic_budget * 0.38, 'percentage': 38},
                        'dining': {'amount': economic_budget * 0.18, 'percentage': 18},
                        'activities': {'amount': economic_budget * 0.12, 'percentage': 12}
                    },
                    'tips': [
                        'Book accommodations in advance for better rates',
                        'Use public transportation when possible',
                        'Try local street food for authentic and affordable meals',
                        'Look for free walking tours and activities',
                        'Visit attractions during off-peak hours for discounts'
                    ]
                },
                {
                    'plan_type': 'Comfort',
                    'description': 'Comfortable travel plan with premium experiences and convenience',
                    'total_budget': comfort_budget,
                    'budget_allocation': {
                        'transportation': {'amount': comfort_budget * 0.28, 'percentage': 28},
                        'accommodation': {'amount': comfort_budget * 0.32, 'percentage': 32},
                        'dining': {'amount': comfort_budget * 0.22, 'percentage': 22},
                        'activities': {'amount': comfort_budget * 0.18, 'percentage': 18}
                    },
                    'tips': [
                        'Book premium accommodations with good amenities',
                        'Consider private transportation for convenience',
                        'Make reservations at recommended restaurants',
                        'Purchase skip-the-line tickets for popular attractions',
                        'Consider guided tours for deeper cultural insights'
                    ]
                }
            ]
            
            logger.info(f"Created {len(plans)} default travel plans")
            return plans
            
        except Exception as e:
            logger.error(f"Error creating default travel plans: {str(e)}")
            return []
    
    def _create_emergency_fallback_plans(self, budget: float, duration: int) -> List[Dict[str, Any]]:
        """Create emergency fallback plans when all other plan generation fails."""
        try:
            logger.warning(f"Creating emergency fallback plans for budget {budget} and duration {duration}")
            
            # Create a single basic plan that will always work
            basic_budget = max(budget, 1000)  # Ensure minimum budget
            basic_duration = max(duration, 1)  # Ensure minimum duration
            
            emergency_plan = {
                'plan_type': 'Basic',
                'description': '基础旅行计划 - 包含必要的旅行安排和预算分配',
                'total_budget': basic_budget,
                'budget_allocation': {
                    'transportation': {'amount': basic_budget * 0.30, 'percentage': 30},
                    'accommodation': {'amount': basic_budget * 0.35, 'percentage': 35},
                    'dining': {'amount': basic_budget * 0.20, 'percentage': 20},
                    'activities': {'amount': basic_budget * 0.15, 'percentage': 15}
                },
                'tips': [
                    '提前规划行程以获得更好的价格',
                    '选择性价比高的住宿和交通方式',
                    '尝试当地美食，体验地道文化',
                    '合理安排时间，平衡观光和休息',
                    '保持灵活性，根据实际情况调整计划'
                ],
                'daily_budget': basic_budget / basic_duration,
                'notes': '这是一个基础的旅行计划模板，建议根据具体目的地和个人喜好进行调整。'
            }
            
            logger.info("Created 1 emergency fallback plan")
            return [emergency_plan]
            
        except Exception as e:
            logger.error(f"Error creating emergency fallback plans: {str(e)}")
            # Return absolute minimum plan
            return [{
                'plan_type': 'Minimal',
                'description': '最基础的旅行计划',
                'total_budget': 1000,
                'budget_allocation': {
                    'transportation': {'amount': 300, 'percentage': 30},
                    'accommodation': {'amount': 350, 'percentage': 35},
                    'dining': {'amount': 200, 'percentage': 20},
                    'activities': {'amount': 150, 'percentage': 15}
                },
                'tips': ['基础旅行建议'],
                'daily_budget': 1000 / 7,
                'notes': '最基础的旅行计划，请根据实际情况调整。'
            }]
    
    def _create_budget_summary(self, travel_plans: List[Dict[str, Any]], total_budget: float) -> Dict[str, Any]:
        """Create a comprehensive budget summary."""
        try:
            if not travel_plans:
                return {'total_budget': total_budget, 'plans': []}
            
            budget_summary = {
                'total_budget': total_budget,
                'currency': 'USD',  # Default currency
                'plans': []
            }
            
            for plan in travel_plans:
                plan_budget = plan.get('total_budget', 0)
                allocation = plan.get('budget_allocation', {})
                
                plan_summary = {
                    'plan_type': plan.get('plan_type', 'Unknown'),
                    'total_budget': plan_budget,
                    'daily_budget': plan_budget / 7,  # Assuming 7 days
                    'allocation': allocation,
                    'savings_vs_total': total_budget - plan_budget if plan_budget < total_budget else 0
                }
                
                budget_summary['plans'].append(plan_summary)
            
            return budget_summary
            
        except Exception as e:
            logger.error(f"Error creating budget summary: {str(e)}")
            return {'total_budget': total_budget, 'plans': []}
    
    def _render_html_template(self, report_data: Dict[str, Any]) -> str:
        """Render the HTML template with report data."""
        try:
            # Try to load custom template first
            try:
                template = self.jinja_env.get_template('travel_plan.html')
                return template.render(**report_data)
            except:
                # Fall back to inline template if file doesn't exist
                return self._render_inline_template(report_data)
                
        except Exception as e:
            logger.error(f"Error rendering HTML template: {str(e)}")
            return self._create_fallback_html(report_data)
    
    def _render_inline_template(self, data: Dict[str, Any]) -> str:
        """Render using inline HTML template."""
        template_str = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body { font-family: 'Microsoft YaHei', 'PingFang SC', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 10px 10px 0 0; text-align: center; }
        .header h1 { margin: 0; font-size: 2.5em; }
        .header .subtitle { font-size: 1.2em; opacity: 0.9; margin-top: 10px; }
        .content { padding: 40px; }
        .section { margin-bottom: 40px; }
        .section h2 { color: #333; border-bottom: 3px solid #667eea; padding-bottom: 10px; }
        .plan-card { background: #f8f9fa; border-left: 5px solid #667eea; padding: 20px; margin: 20px 0; border-radius: 5px; }
        .plan-card h3 { color: #667eea; margin-top: 0; }
        .budget-item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }
        .attraction-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .attraction-card { background: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .tips-list { background: #e8f4f8; padding: 20px; border-radius: 8px; }
        .tips-list ul { margin: 0; padding-left: 20px; }
        .weather-forecast { display: flex; gap: 15px; overflow-x: auto; padding: 20px 0; }
        .weather-day { background: #f0f8ff; padding: 15px; border-radius: 8px; min-width: 120px; text-align: center; }
        .footer { background: #333; color: white; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; }
        .ai-insights { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 5px solid #28a745; line-height: 1.8; }
        .ai-insights h3 { color: #28a745; margin-bottom: 15px; }
        @media (max-width: 768px) { .container { margin: 10px; } .content { padding: 20px; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ title }}</h1>
            <div class="subtitle">您的个性化旅行指南</div>
            <div style="margin-top: 15px;">
                📍 {{ destination }} | 📅 {{ start_date }} | ⏱️ {{ duration }} 天 | 💰 ¥{{ "%.2f"|format(budget) }}
            </div>
            <div style="margin-top: 15px; opacity: 0.8;">
                生成时间：{{ generation_date }}
            </div>
        </div>
        
        <div class="content">
            <!-- Destination Overview -->
            <div class="section">
                <h2>🌍 目的地概览</h2>
                <p>{{ destination_introduction or '欢迎来到这个充满魅力的旅行目的地！这里拥有丰富的历史文化、独特的自然风光和令人难忘的旅行体验。' }}</p>
                {% if destination_info %}
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px;">
                    <div><strong>最佳旅行时间:</strong> 
                        {% if destination_info.best_time_to_visit == 'Spring and Fall' %}春秋两季
                        {% elif destination_info.best_time_to_visit == 'Year-round' %}全年适宜
                        {% else %}{{ destination_info.best_time_to_visit or '春秋两季' }}
                        {% endif %}
                    </div>
                    <div><strong>当地货币:</strong> 
                        {% if destination_info.local_currency == 'Local Currency' %}人民币
                        {% else %}{{ destination_info.local_currency or '人民币' }}
                        {% endif %}
                    </div>
                    <div><strong>语言:</strong> 
                        {% if destination_info.language == 'Local Language' %}中文
                        {% else %}{{ destination_info.language or '中文' }}
                        {% endif %}
                    </div>
                    <div><strong>安全等级:</strong> 
                        {% if destination_info.safety_rating == 'Generally Safe' %}总体安全
                        {% else %}{{ destination_info.safety_rating or '总体安全' }}
                        {% endif %}
                    </div>
                </div>
                {% endif %}
            </div>

            <!-- Travel Plans -->
            <div class="section">
                <h2>📋 旅行计划 ({{ plans_count }} 个选项)</h2>
                {% for plan in travel_plans %}
                <div class="plan-card">
                    <h3>
                        {% if plan.plan_type == 'Economic' %}经济型
                        {% elif plan.plan_type == 'Comfort' %}舒适型
                        {% elif plan.plan_type == 'Luxury' %}豪华型
                        {% else %}{{ plan.plan_type }}
                        {% endif %} 计划 - ¥{{ "%.2f"|format(plan.total_budget) }}
                    </h3>
                    <p>
                        {% if 'Budget-friendly' in (plan.description or '') %}注重性价比的经济型旅行计划，专注于核心体验和必游景点
                        {% elif 'Comfortable' in (plan.description or '') %}舒适便捷的旅行计划，提供优质体验和贴心服务
                        {% elif 'Luxury' in (plan.description or '') %}豪华尊享的旅行计划，提供顶级服务和独特体验
                        {% else %}{{ plan.description or '为您精心定制的旅行计划，确保完美的旅行体验' }}
                        {% endif %}
                    </p>
                    
                    <h4>💰 预算分配：</h4>
                    {% for category, details in plan.budget_allocation.items() %}
                    <div class="budget-item">
                        <span>
                            {% if category == 'transportation' %}交通费用
                            {% elif category == 'accommodation' %}住宿费用
                            {% elif category == 'dining' %}餐饮费用
                            {% elif category == 'activities' %}活动费用
                            {% elif category == 'shopping' %}购物费用
                            {% else %}{{ category.replace('_', ' ').title() }}
                            {% endif %}:
                        </span>
                        <span>¥{{ "%.2f"|format(details.amount) }} ({{ details.percentage }}%)</span>
                    </div>
                    {% endfor %}
                    
                    <div class="tips-list" style="margin-top: 20px;">
                        <h4>💡 此计划的建议：</h4>
                        <ul>
                        {% for tip in plan.tips %}
                            <li>
                                {% if 'Book accommodations in advance' in tip %}提前预订住宿以获得更好的价格
                                {% elif 'Use public transportation' in tip %}尽可能使用公共交通工具
                                {% elif 'Try local street food' in tip %}尝试当地街头美食，体验正宗且实惠的餐饮
                                {% elif 'Look for free walking tours' in tip %}寻找免费的步行游览和活动
                                {% elif 'Visit attractions during off-peak' in tip %}在非高峰时段参观景点以获得折扣
                                {% elif 'Book premium accommodations' in tip %}预订设施完善的优质住宿
                                {% elif 'Consider private transportation' in tip %}考虑私人交通工具以获得便利
                                {% elif 'Make reservations at recommended' in tip %}在推荐餐厅提前预订
                                {% elif 'Purchase skip-the-line tickets' in tip %}购买热门景点的免排队门票
                                {% elif 'Consider guided tours' in tip %}考虑参加导游服务以获得更深入的文化体验
                                {% else %}{{ tip }}
                                {% endif %}
                            </li>
                        {% endfor %}
                        </ul>
                    </div>
                </div>
                {% endfor %}
            </div>

            <!-- Weather Forecast -->
            <div class="section">
                <h2>🌤️ 天气预报</h2>
                {% if weather_forecast and weather_forecast|length > 0 %}
                <div class="weather-forecast">
                    {% for day in weather_forecast[:7] %}
                    <div class="weather-day">
                        <div><strong>{{ day.date or '第' + loop.index|string + '天' }}</strong></div>
                        <div>
                            {% if day.condition == 'Sunny' %}晴天
                            {% elif day.condition == 'Cloudy' %}多云
                            {% elif day.condition == 'Clear' %}晴朗
                            {% elif day.condition == 'Partly Cloudy' %}局部多云
                            {% elif day.condition == 'Rainy' %}雨天
                            {% else %}{{ day.condition or '多云' }}
                            {% endif %}
                        </div>
                        <div>{{ day.temperature or '22' }}°C</div>
                    </div>
                    {% endfor %}
                </div>
                {% if weather_info and weather_info.source %}
                <div style="margin-top: 15px; padding: 10px; background: #e8f5e8; border-radius: 5px; font-size: 0.9em;">
                    <strong>数据来源:</strong> {{ weather_info.source }}
                    {% if weather_info.note %}
                    <br><strong>说明:</strong> {{ weather_info.note }}
                    {% endif %}
                </div>
                {% endif %}
                {% else %}
                <div style="padding: 20px; background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; margin: 20px 0;">
                    <h4 style="color: #856404; margin-top: 0;">⚠️ 天气信息暂时无法获取</h4>
                    {% if weather_info and weather_info.error %}
                    <p style="color: #856404; margin-bottom: 10px;">
                        <strong>错误信息:</strong> {{ weather_info.error }}
                    </p>
                    {% endif %}
                    {% if weather_info and weather_info.note %}
                    <p style="color: #856404; margin-bottom: 10px;">
                        {{ weather_info.note }}
                    </p>
                    {% endif %}
                    {% if weather_info and weather_info.suggestion %}
                    <p style="color: #856404; margin-bottom: 0;">
                        <strong>建议:</strong> {{ weather_info.suggestion }}
                    </p>
                    {% endif %}
                    <p style="color: #856404; margin-bottom: 0;">
                        <strong>建议:</strong> 请在出行前通过天气应用或网站查看最新天气预报，以便做好相应准备。
                    </p>
                </div>
                {% endif %}
            </div>

            <!-- Top Attractions -->
            {% if attractions %}
            <div class="section">
                <h2>🎯 热门景点</h2>
                <div class="attraction-grid">
                    {% for attraction in attractions %}
                    <div class="attraction-card">
                        <h4>
                            {% if 'Observatory Deck' in (attraction.name or '') %}{{ destination }}观景台
                            {% elif 'Historic Center' in (attraction.name or '') %}{{ destination }}历史中心
                            {% elif 'Central Park' in (attraction.name or '') %}{{ destination }}中央公园
                            {% elif 'Waterfront Promenade' in (attraction.name or '') %}{{ destination }}滨水步道
                            {% elif 'Art Museum' in (attraction.name or '') %}{{ destination }}艺术博物馆
                            {% elif 'Local Market' in (attraction.name or '') %}{{ destination }}当地市场
                            {% else %}{{ attraction.name or '当地景点' }}
                            {% endif %}
                        </h4>
                        <p>
                            {% if 'Panoramic city views' in (attraction.description or '') %}全景城市观景台，可欣赏到城市最美的全景视野，特别是日出日落时分景色格外迷人。
                            {% elif 'historic heart of the city' in (attraction.description or '') %}探索城市历史中心，这里有数百年历史的古建筑、迷人的街道和讲述地区故事的文化地标。
                            {% elif 'Beautiful urban park' in (attraction.description or '') %}美丽的城市公园，是放松休闲、野餐和户外活动的完美场所。设有花园、步行道和娱乐设施。
                            {% elif 'Scenic waterfront area' in (attraction.description or '') %}风景优美的滨水区域，适合悠闲漫步、用餐和欣赏水景。是当地人和游客都喜爱的热门景点。
                            {% elif 'World-class art collection' in (attraction.description or '') %}世界级艺术收藏，展示本地和国际艺术家作品，设有轮换展览和常设画廊，展现该地区的文化遗产。
                            {% elif 'Vibrant local market' in (attraction.description or '') %}充满活力的当地市场，您可以体验正宗文化、品尝当地美食、购买独特纪念品和手工艺品。
                            {% else %}{{ attraction.description or '必游目的地，拥有独特体验和文化意义。' }}
                            {% endif %}
                        </p>
                        <div style="margin-top: 15px;">
                            <div><strong>评分:</strong> ⭐ {{ attraction.rating or '4.5' }}/5</div>
                            <div><strong>游览时长:</strong> 
                                {% if 'hours' in (attraction.duration or '') %}{{ attraction.duration|replace('hours', '小时')|replace('hour', '小时')|replace('-', ' - ') }}
                                {% else %}{{ attraction.duration or '2-3小时' }}
                                {% endif %}
                            </div>
                            {% if attraction.entrance_fee %}
                            <div><strong>门票:</strong> ¥{{ attraction.entrance_fee }}</div>
                            {% else %}
                            <div><strong>门票:</strong> 免费</div>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            <!-- Dining Recommendations -->
            {% if dining_options %}
            <div class="section">
                <h2>🍽️ 餐饮推荐</h2>
                <div class="attraction-grid">
                    {% for restaurant in dining_options %}
                    <div class="attraction-card">
                        <h4>
                            {% if 'Local Specialty Restaurant' in (restaurant.name or '') %}当地特色餐厅
                            {% elif 'Street Food Market' in (restaurant.name or '') %}街头美食市场
                            {% elif 'Fine Dining Experience' in (restaurant.name or '') %}高端餐饮体验
                            {% else %}{{ restaurant.name or '当地餐厅' }}
                            {% endif %}
                        </h4>
                        <p><strong>菜系:</strong> 
                            {% if restaurant.cuisine == 'Local Cuisine' %}当地菜系
                            {% elif restaurant.cuisine == 'Street Food' %}街头小食
                            {% elif restaurant.cuisine == 'International' %}国际料理
                            {% else %}{{ restaurant.cuisine or '当地菜系' }}
                            {% endif %}
                        </p>
                        <p><strong>价格区间:</strong> 
                            {% if restaurant.price_range == 'Budget' %}经济实惠
                            {% elif restaurant.price_range == 'Mid-range' %}中等价位
                            {% elif restaurant.price_range == 'High-end' %}高端消费
                            {% else %}{{ restaurant.price_range or '中等价位' }}
                            {% endif %}
                        </p>
                        <p><strong>评分:</strong> ⭐ {{ restaurant.rating or '4.2' }}/5</p>
                        {% if restaurant.specialties %}
                        <p><strong>招牌菜:</strong> 
                            {% set chinese_specialties = [] %}
                            {% for specialty in restaurant.specialties %}
                                {% if specialty == 'Local Dish 1' %}{% set _ = chinese_specialties.append('招牌菜1') %}
                                {% elif specialty == 'Local Dish 2' %}{% set _ = chinese_specialties.append('招牌菜2') %}
                                {% elif specialty == 'Street Snacks' %}{% set _ = chinese_specialties.append('街头小食') %}
                                {% elif specialty == 'Local Beverages' %}{% set _ = chinese_specialties.append('当地饮品') %}
                                {% elif specialty == 'Signature Dishes' %}{% set _ = chinese_specialties.append('招牌菜品') %}
                                {% elif specialty == 'Wine Pairing' %}{% set _ = chinese_specialties.append('配酒套餐') %}
                                {% else %}{% set _ = chinese_specialties.append(specialty) %}
                                {% endif %}
                            {% endfor %}
                            {{ chinese_specialties|join(', ') }}
                        </p>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            <!-- Practical Information -->
            <div class="section">
                <h2>ℹ️ 实用信息</h2>
                
                {% if useful_phrases %}
                <div style="margin-bottom: 30px;">
                    <h3>🗣️ 常用语句</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                        {% for phrase in useful_phrases %}
                        <div style="background: #f0f8ff; padding: 10px; border-radius: 5px;">
                            {% if phrase == 'Hello' %}你好
                            {% elif phrase == 'Thank you' %}谢谢
                            {% elif phrase == 'Excuse me' %}不好意思
                            {% elif phrase == 'How much?' %}多少钱？
                            {% else %}{{ phrase }}
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}

                <div style="margin-bottom: 30px;">
                    <h3>🚨 紧急联系电话</h3>
                    <div style="background: #ffe6e6; padding: 10px; margin: 5px 0; border-radius: 5px;">🚔 报警电话：110</div>
                    <div style="background: #ffe6e6; padding: 10px; margin: 5px 0; border-radius: 5px;">🚑 急救电话：120</div>
                    <div style="background: #ffe6e6; padding: 10px; margin: 5px 0; border-radius: 5px;">🚒 火警电话：119</div>
                    <div style="background: #ffe6e6; padding: 10px; margin: 5px 0; border-radius: 5px;">🚨 旅游投诉：12301</div>
                </div>

                {% if cultural_etiquette %}
                <div class="tips-list">
                    <h3>🤝 文化礼仪</h3>
                    <ul>
                    {% for tip in cultural_etiquette %}
                        <li>{{ tip }}</li>
                    {% endfor %}
                    </ul>
                </div>
                {% endif %}
            </div>

            <!-- AI Insights -->
            {% if ai_insights %}
            <div class="section">
                <h2>🤖 AI 旅行洞察</h2>
                <div class="ai-insights">
                    <h3>个性化推荐</h3>
                    <div class="ai-insights-content">
                        {{ ai_insights|safe }}
                    </div>
                </div>
            </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>由 <strong>AI 旅行助手</strong> v1.0 生成</p>
            <p>
                <span style="font-size: 1.5em; margin: 0 5px;">✈️</span>
                祝您旅途愉快！
                <span style="font-size: 1.5em; margin: 0 5px;">🌟</span>
            </p>
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(template_str)
        return template.render(**data)
    
    def _create_fallback_html(self, data: Dict[str, Any]) -> str:
        """Create a basic fallback HTML if template rendering fails."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Travel Plan - {data.get('destination', 'Unknown')}</title>
    <style>body {{ font-family: Arial, sans-serif; margin: 40px; }}</style>
</head>
<body>
    <h1>Travel Plan for {data.get('destination', 'Unknown Destination')}</h1>
    <p><strong>Date:</strong> {data.get('start_date', 'TBD')}</p>
    <p><strong>Duration:</strong> {data.get('duration', 'N/A')} days</p>
    <p><strong>Budget:</strong> ${data.get('budget', 0):.2f}</p>
    <p><strong>Generated:</strong> {data.get('generation_date', 'Unknown')}</p>
    
    <h2>Travel Plans</h2>
    <p>{len(data.get('travel_plans', []))} travel plan(s) generated.</p>
    
    <p><em>This is a simplified version. Please check the logs for any template rendering issues.</em></p>
</body>
</html>
        """
    
    def _save_html_report(self, html_content: str, destination: str, start_date: str) -> str:
        """Save the HTML report to a file."""
        try:
            # Create output directory if it doesn't exist
            output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename
            safe_destination = "".join(c for c in destination if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_destination = safe_destination.replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"travel_plan_{safe_destination}_{start_date}_{timestamp}.html"
            
            file_path = os.path.join(output_dir, filename)
            
            # Write HTML content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report saved to: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving HTML report: {str(e)}")
            raise
