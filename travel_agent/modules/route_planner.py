import random
from typing import Dict, Any, List
from datetime import datetime, timedelta

from config.settings import BUDGET_ALLOCATION

class RoutePlanner:
    """负责根据预算、时间、天气等因素生成智能旅行规划。"""

    def __init__(self):
        pass

    def generate_plan(self, travel_info: Dict[str, Any], weather_forecast: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成一个详细的旅行规划方案。
        Args:
            travel_info: 包含出发城市、目的地、日期、天数、预算等信息的字典。
            weather_forecast: 目的地未来几天的天气预报。
        Returns:
            包含完整旅行规划的字典。
        """
        destination = travel_info["destination"]
        duration = travel_info["duration"]
        total_budget = travel_info["budget"]
        departure_date_str = travel_info["departure_date"]
        departure_date = datetime.strptime(departure_date_str, "%Y-%m-%d")

        # 1. 预算分配
        allocated_budget = self._allocate_budget(total_budget)

        # 2. 生成每日行程
        daily_plans = []
        for i in range(duration):
            current_date = departure_date + timedelta(days=i)
            current_date_str = current_date.strftime("%Y-%m-%d")

            # 获取当日天气信息
            day_weather = next((w for w in weather_forecast if w["date"] == current_date_str), {})
            if not day_weather:
                # 如果没有找到当天的天气预报，使用默认值或进行提示
                day_weather = {
                    "date": current_date_str,
                    "conditions": "未知",
                    "icon": "❓",
                    "min_temp": "N/A",
                    "max_temp": "N/A",
                    "suggestions": "",
                    "clothing_suggestions": "",
                    "activity_recommendations": ""
                }

            # 根据天气调整活动
            activity_suggestions, clothing_suggestions = self._get_weather_based_suggestions(day_weather)

            daily_plans.append({
                "date": current_date_str,
                "summary": f"探索{destination}的第{i+1}天",
                "weather_icon": day_weather.get("icon", "❓"),
                "weather_conditions": day_weather.get("conditions", "未知"),
                "weather_class": self._get_weather_class(day_weather.get("conditions", "")), # 用于CSS样式
                "clothing_suggestions": clothing_suggestions,
                "activity_recommendations": activity_suggestions,
                "attractions": self._generate_attractions(destination, allocated_budget["attractions"] / duration, day_weather),
                "meals": self._generate_meals(destination, allocated_budget["dining"] / duration)
            })

        # 3. 交通和住宿 (简化处理，实际应根据预算和天数动态生成)
        transportation = self._generate_transportation(travel_info["departure_city"], destination, allocated_budget["transportation"])
        accommodation = self._generate_accommodation(destination, allocated_budget["accommodation"] / duration)

        # 4. 美食推荐 (示例)
        food_recommendations = [
            {"name": "当地特色小吃", "description": "品尝地道风味", "price_range": "¥20-50", "image_url": "https://via.placeholder.com/300x200?text=Local+Food"},
            {"name": "海鲜大餐", "description": "新鲜海产，不容错过", "price_range": "¥100-300", "image_url": "https://via.placeholder.com/300x200?text=Seafood"},
        ]

        # 5. 天气概况总结
        weather_summary = self._summarize_weather(weather_forecast)

        return {
            "departure_city": travel_info["departure_city"],
            "destination": destination,
            "departure_date": departure_date_str,
            "duration": duration,
            "budget": total_budget,
            "plan_type": "舒适型", # 示例，后续可根据预算和用户偏好调整
            "allocated_budget": allocated_budget,
            "weather_summary": weather_summary,
            "weather_forecast": weather_forecast, # 传递完整的预报数据用于详细表格
            "daily_plans": daily_plans,
            "transportation": transportation,
            "accommodation": accommodation,
            "food_recommendations": food_recommendations,
            "clothing_suggestions": self._get_overall_clothing_suggestions(weather_forecast),
            "budget_chart_url": "https://quickchart.io/chart?c={type:'pie',data:{labels:['交通','住宿','餐饮','景点'],datasets:[{data:[30,40,20,10]}]}}" # 示例饼图URL
        }

    def _allocate_budget(self, total_budget: float) -> Dict[str, float]:
        """
        根据预设比例分配预算。
        """
        allocated = {}
        for category, percentage in BUDGET_ALLOCATION.items():
            allocated[category] = total_budget * percentage
        return allocated

    def _generate_attractions(self, destination: str, daily_attraction_budget: float, day_weather: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        生成每日景点列表，并根据天气调整。
        """
        attractions = []
        # 模拟景点数据
        if "雨" in day_weather.get("conditions", "") or "阴" in day_weather.get("conditions", ""):
            # 阴雨天推荐室内景点
            attractions.append({
                "name": f"{destination}博物馆",
                "description": "了解当地历史文化",
                "ticket_price": random.uniform(30, 80),
                "opening_hours": "09:00 - 17:00",
                "image_url": "https://via.placeholder.com/300x200?text=Museum",
                "weather_icon": day_weather.get("icon", "❓"),
                "weather_conditions": day_weather.get("conditions", "未知"),
                "temperature": day_weather.get("max_temp", "N/A"),
                "activity_suitability": "适合室内活动"
            })
        else:
            # 晴天推荐户外景点
            attractions.append({
                "name": f"{destination}公园",
                "description": "享受自然风光",
                "ticket_price": random.uniform(0, 50),
                "opening_hours": "全天开放",
                "image_url": "https://via.placeholder.com/300x200?text=Park",
                "weather_icon": day_weather.get("icon", "❓"),
                "weather_conditions": day_weather.get("conditions", "未知"),
                "temperature": day_weather.get("max_temp", "N/A"),
                "activity_suitability": "适合户外活动"
            })
        return attractions

    def _generate_meals(self, destination: str, daily_dining_budget: float) -> List[Dict[str, Any]]:
        """
        生成每日餐饮安排。
        """
        meals = [
            {"type": "早餐", "restaurant_name": "酒店餐厅", "dishes": "自助餐", "estimated_cost": random.uniform(20, 50)},
            {"type": "午餐", "restaurant_name": f"{destination}特色餐厅", "dishes": "当地美食", "estimated_cost": random.uniform(50, 150)},
            {"type": "晚餐", "restaurant_name": "人气小吃街", "dishes": "各种小吃", "estimated_cost": random.uniform(30, 100)},
        ]
        return meals

    def _generate_transportation(self, origin: str, destination: str, budget: float) -> Dict[str, Any]:
        """
        生成交通信息。
        """
        return {
            "type": "飞机",
            "estimated_cost": budget,
            "duration": "3小时",
            "notes": "建议提前预订机票"
        }

    def _generate_accommodation(self, destination: str, daily_budget: float) -> Dict[str, Any]:
        """
        生成住宿信息。
        """
        return {
            "name": "舒适酒店",
            "price_range": daily_budget,
            "address": f"{destination}市中心",
            "notes": "含早餐，交通便利"
        }

    def _summarize_weather(self, weather_forecast: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        总结旅行期间的天气概况。
        """
        if not weather_forecast: return {}

        min_temps = [d["min_temp"] for d in weather_forecast if isinstance(d["min_temp"], (int, float))]
        max_temps = [d["max_temp"] for d in weather_forecast if isinstance(d["max_temp"], (int, float))]
        conditions = [d["conditions"] for d in weather_forecast]
        rain_probs = [d["rain_probability"] for d in weather_forecast if isinstance(d["rain_probability"], (int, float))]
        aqi_values = [d["aqi"] for d in weather_forecast if d["aqi"] != "N/A"]
        uv_indices = [d["uv_index"] for d in weather_forecast if d["uv_index"] != "N/A"]

        temp_range = f"{min(min_temps) if min_temps else 'N/A'}°C - {max(max_temps) if max_temps else 'N/A'}°C"
        weather_trend = ", ".join(list(set(conditions))) # 去重后连接
        avg_rain_prob = f"{sum(rain_probs) / len(rain_probs):.0f}%" if rain_probs else "N/A"
        avg_aqi = aqi_values[0] if aqi_values else "N/A" # 简化处理，实际应计算平均或最常见
        avg_uv_index = uv_indices[0] if uv_indices else "N/A" # 简化处理

        return {
            "temp_range": temp_range,
            "weather_trend": weather_trend,
            "rain_probability": avg_rain_prob,
            "aqi": avg_aqi,
            "uv_index": avg_uv_index,
        }

    def _get_weather_based_suggestions(self, day_weather: Dict[str, Any]) -> (str, str):
        """
        根据天气提供穿搭和活动建议。
        """
        conditions = day_weather.get("conditions", "未知")
        max_temp = day_weather.get("max_temp", "N/A")
        min_temp = day_weather.get("min_temp", "N/A")

        clothing_suggestions = ""
        activity_recommendations = ""

        if "雨" in conditions or "雷" in conditions:
            clothing_suggestions = "请携带雨具，穿着防水衣物。"
            activity_recommendations = "建议安排室内活动，如参观博物馆、艺术馆或购物中心。"
        elif "晴" in conditions:
            clothing_suggestions = "穿着轻便透气的衣物，注意防晒。"
            activity_recommendations = "适合户外活动，如公园散步、景点游览。"
        elif "多云" in conditions or "阴" in conditions:
            clothing_suggestions = "穿着舒适的衣物，可备一件薄外套。"
            activity_recommendations = "室内外活动皆可，注意天气变化。"
        elif "雪" in conditions:
            clothing_suggestions = "穿着保暖的羽绒服、雪地靴，注意防滑。"
            activity_recommendations = "适合滑雪、温泉等冬季活动。"
        else:
            clothing_suggestions = "根据气温选择合适衣物。"
            activity_recommendations = "灵活安排行程。"
        
        if isinstance(max_temp, (int, float)) and max_temp >= 30:
            clothing_suggestions += " 天气炎热，注意防暑降温。"
            activity_recommendations += " 避免在中午时段进行剧烈户外活动。"
        elif isinstance(min_temp, (int, float)) and min_temp <= 5:
            clothing_suggestions += " 天气寒冷，注意保暖。"

        return activity_recommendations, clothing_suggestions

    def _get_overall_clothing_suggestions(self, weather_forecast: List[Dict[str, Any]]) -> List[str]:
        """
        根据整个旅行期间的天气预报，提供整体穿搭建议。
        """
        if not weather_forecast: return ["根据每日天气预报调整穿搭。"]

        all_conditions = [d["conditions"] for d in weather_forecast]
        all_min_temps = [d["min_temp"] for d in weather_forecast if isinstance(d["min_temp"], (int, float))]
        all_max_temps = [d["max_temp"] for d in weather_forecast if isinstance(d["max_temp"], (int, float))]

        suggestions = []

        if any("雨" in c for c in all_conditions) or any("雷" in c for c in all_conditions):
            suggestions.append("请务必携带雨具（雨伞或雨衣）和防水鞋。")
        if any("雪" in c for c in all_conditions):
            suggestions.append("准备厚实的冬季衣物、防滑鞋和保暖配件。")

        if all_max_temps and max(all_max_temps) >= 30:
            suggestions.append("多带轻薄透气的夏季衣物，注意防晒和防暑。")
        if all_min_temps and min(all_min_temps) <= 10:
            suggestions.append("准备保暖衣物，如毛衣、外套或薄羽绒服。")

        if not suggestions:
            suggestions.append("根据每日具体天气预报，灵活搭配衣物。")

        return suggestions

    def _get_weather_class(self, conditions: str) -> str:
        """
        根据天气状况返回对应的CSS类名。
        """
        if "晴" in conditions: return "sunny"
        if "云" in conditions or "阴" in conditions: return "cloudy"
        if "雨" in conditions: return "rainy"
        if "雪" in conditions: return "snowy"
        if "雷" in conditions: return "thunderstorm"
        return ""

# 示例用法 (仅用于测试)
async def main():
    planner = RoutePlanner()
    travel_info = {
        "departure_city": "北京",
        "destination": "三亚",
        "departure_date": "2025-08-01",
        "duration": 3,
        "budget": 3000
    }
    # 模拟天气预报数据
    weather_forecast = [
        {"date": "2025-08-01", "conditions": "晴", "icon": "☀️", "min_temp": 25, "max_temp": 32, "suggestions": "", "clothing_suggestions": "", "activity_recommendations": ""},
        {"date": "2025-08-02", "conditions": "多云", "icon": "☁️", "min_temp": 26, "max_temp": 31, "suggestions": "", "clothing_suggestions": "", "activity_recommendations": ""},
        {"date": "2025-08-03", "conditions": "雷阵雨", "icon": "⛈️", "min_temp": 24, "max_temp": 29, "suggestions": "", "clothing_suggestions": "", "activity_recommendations": ""},
    ]
    plan = planner.generate_plan(travel_info, weather_forecast)
    # print(plan)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
