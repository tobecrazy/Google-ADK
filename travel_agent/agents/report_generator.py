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
            # Extract key information
            destination_info = travel_data.get('destination_info', {})
            weather_data = travel_data.get('weather_data', {})
            attractions = travel_data.get('attractions', [])
            accommodations = travel_data.get('accommodations', [])
            dining = travel_data.get('dining', [])
            transportation = travel_data.get('transportation', {})
            local_info = travel_data.get('local_info', {})
            ai_insights = travel_data.get('ai_insights', {})
            
            report_data = {
                # Header Information
                'title': f'Travel Plan for {destination}',
                'destination': destination,
                'start_date': start_date,
                'duration': duration,
                'budget': budget,
                'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                
                # Destination Overview
                'destination_info': destination_info,
                'weather_forecast': weather_data.get('forecast', []),
                
                # Travel Plans
                'travel_plans': travel_plans,
                'plans_count': len(travel_plans),
                
                # Transportation
                'transportation_options': transportation.get('intercity_options', {}),
                'transportation_recommendation': transportation.get('recommendation', {}),
                'local_transport': transportation.get('local_transport', {}),
                
                # Attractions & Activities
                'attractions': attractions[:10],  # Top 10 attractions
                'attractions_count': len(attractions),
                
                # Accommodations
                'accommodations': accommodations[:5],  # Top 5 accommodations
                
                # Dining
                'dining_options': dining[:8],  # Top 8 dining options
                
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
            
            return report_data
            
        except Exception as e:
            logger.error(f"Error preparing report data: {str(e)}")
            return {}
    
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
                    'ai_insights': ai_response  # Use the full AI response for insights
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 10px 10px 0 0; }
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
        @media (max-width: 768px) { .container { margin: 10px; } .content { padding: 20px; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ title }}</h1>
            <div class="subtitle">
                📍 {{ destination }} | 📅 {{ start_date }} | ⏱️ {{ duration }} days | 💰 ${{ "%.2f"|format(budget) }}
            </div>
            <div style="margin-top: 15px; opacity: 0.8;">
                Generated on {{ generation_date }}
            </div>
        </div>
        
        <div class="content">
            <!-- Destination Overview -->
            <div class="section">
                <h2>🌍 Destination Overview</h2>
                <p>{{ destination_introduction }}</p>
                {% if destination_info %}
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px;">
                    <div><strong>Best Time to Visit:</strong> {{ destination_info.best_time_to_visit or 'Year-round' }}</div>
                    <div><strong>Local Currency:</strong> {{ destination_info.local_currency or 'Local Currency' }}</div>
                    <div><strong>Language:</strong> {{ destination_info.language or 'Local Language' }}</div>
                    <div><strong>Safety Rating:</strong> {{ destination_info.safety_rating or 'Generally Safe' }}</div>
                </div>
                {% endif %}
            </div>

            <!-- Travel Plans -->
            <div class="section">
                <h2>📋 Travel Plans ({{ plans_count }} options)</h2>
                {% for plan in travel_plans %}
                <div class="plan-card">
                    <h3>{{ plan.plan_type }} Plan - ${{ "%.2f"|format(plan.total_budget) }}</h3>
                    <p>{{ plan.description }}</p>
                    
                    <h4>Budget Allocation:</h4>
                    {% for category, details in plan.budget_allocation.items() %}
                    <div class="budget-item">
                        <span>{{ category.title() }}:</span>
                        <span>${{ "%.2f"|format(details.amount) }} ({{ details.percentage }}%)</span>
                    </div>
                    {% endfor %}
                    
                    <div class="tips-list" style="margin-top: 20px;">
                        <h4>💡 Tips for this plan:</h4>
                        <ul>
                        {% for tip in plan.tips %}
                            <li>{{ tip }}</li>
                        {% endfor %}
                        </ul>
                    </div>
                </div>
                {% endfor %}
            </div>

            <!-- Weather Forecast -->
            {% if weather_forecast %}
            <div class="section">
                <h2>🌤️ Weather Forecast</h2>
                <div class="weather-forecast">
                    {% for day in weather_forecast[:7] %}
                    <div class="weather-day">
                        <div><strong>{{ day.date or 'Day ' + loop.index|string }}</strong></div>
                        <div>{{ day.condition or 'Partly Cloudy' }}</div>
                        <div>{{ day.temperature or '22°C' }}</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            <!-- Top Attractions -->
            {% if attractions %}
            <div class="section">
                <h2>🎯 Top Attractions</h2>
                <div class="attraction-grid">
                    {% for attraction in attractions %}
                    <div class="attraction-card">
                        <h4>{{ attraction.name or 'Local Attraction' }}</h4>
                        <p>{{ attraction.description or 'A must-visit destination with unique experiences.' }}</p>
                        <div style="margin-top: 15px;">
                            <div><strong>Rating:</strong> ⭐ {{ attraction.rating or '4.5' }}/5</div>
                            <div><strong>Duration:</strong> {{ attraction.duration or '2-3 hours' }}</div>
                            {% if attraction.price %}
                            <div><strong>Price:</strong> ${{ attraction.price }}</div>
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
                <h2>🍽️ Dining Recommendations</h2>
                <div class="attraction-grid">
                    {% for restaurant in dining_options %}
                    <div class="attraction-card">
                        <h4>{{ restaurant.name or 'Local Restaurant' }}</h4>
                        <p><strong>Cuisine:</strong> {{ restaurant.cuisine or 'Local Cuisine' }}</p>
                        <p><strong>Price Range:</strong> {{ restaurant.price_range or 'Mid-range' }}</p>
                        <p><strong>Rating:</strong> ⭐ {{ restaurant.rating or '4.2' }}/5</p>
                        {% if restaurant.specialties %}
                        <p><strong>Specialties:</strong> {{ restaurant.specialties|join(', ') }}</p>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            <!-- Practical Information -->
            <div class="section">
                <h2>ℹ️ Practical Information</h2>
                
                {% if useful_phrases %}
                <div style="margin-bottom: 30px;">
                    <h3>🗣️ Useful Phrases</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                        {% for phrase in useful_phrases %}
                        <div style="background: #f0f8ff; padding: 10px; border-radius: 5px;">{{ phrase }}</div>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}

                {% if emergency_numbers %}
                <div style="margin-bottom: 30px;">
                    <h3>🚨 Emergency Contacts</h3>
                    {% for contact in emergency_numbers %}
                    <div style="background: #ffe6e6; padding: 10px; margin: 5px 0; border-radius: 5px;">{{ contact }}</div>
                    {% endfor %}
                </div>
                {% endif %}

                {% if cultural_etiquette %}
                <div class="tips-list">
                    <h3>🤝 Cultural Etiquette</h3>
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
                <h2>🤖 AI Travel Insights</h2>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 5px solid #28a745;">
                    {{ ai_insights }}
                </div>
            </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>Generated by Travel AI Agent | {{ meta.generated_by }} v{{ meta.version }}</p>
            <p>Have an amazing trip! 🌟</p>
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
