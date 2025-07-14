# config/prompts.py

# Prompts for AI Agent

WEATHER_SUMMARY_PROMPT = """
根据以下天气数据，生成一段简洁的旅行期间天气概况，包括温度范围、天气趋势、降雨概率、空气质量指数(AQI)和紫外线指数。

天气数据：
{weather_data}

天气概况：
"""

CLOTHING_SUGGESTION_PROMPT = """
根据以下天气数据和旅行日期，为旅行者提供详细的穿搭建议。考虑温度、降雨、风力、紫外线等因素。

天气数据：
{weather_data}

旅行日期：{travel_date}

穿搭建议：
"""

ACTIVITY_RECOMMENDATION_PROMPT = """
根据以下天气数据和旅行目的地信息，为旅行者推荐适合的活动。考虑天气对室内外活动的影响，并提供备选方案。

天气数据：
{weather_data}

目的地信息：
{destination_info}

活动建议：
"""

DAILY_SUMMARY_PROMPT = """
根据以下每日行程和天气信息，生成一个简洁的每日总结。

日期：{date}
天气：{weather_conditions}
最高温：{max_temp}°C
最低温：{min_temp}°C
景点：{attractions}

每日总结：
"""

BUDGET_ALLOCATION_PROMPT = """
根据总预算 {total_budget} 元和以下预算分配比例，计算各项（交通、住宿、餐饮、景点）的预算金额。返回JSON格式。

预算分配比例：
{allocation_percentages}

"""
