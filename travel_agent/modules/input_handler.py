import json
from typing import Dict
import datetime
import google.generativeai as genai
import re

class InputHandler:
    def __init__(self):
        # Initialize the generative model
        # Ensure that genai.configure(api_key="YOUR_API_KEY") has been called elsewhere
        self.model = genai.GenerativeModel('gemini-pro') # Using gemini-pro for text generation

    def parse_input(self, user_input: str) -> Dict:
        """Parses the user input to extract travel information."""
        try:
            # Try parsing as JSON first
            return json.loads(user_input)
        except json.JSONDecodeError:
            pass # Not JSON, continue to next parsing method

        # Try parsing as space-separated values
        parts = user_input.split()
        if len(parts) >= 2 and parts[0] not in ["规划", "计划", "安排"] and parts[1] not in ["一下", "去"]:
            try:
                return {
                    "departure_city": parts[0],
                    "destination": parts[1],
                    "departure_date": parts[2] if len(parts) > 2 else str(datetime.date.today()),
                    "duration": int(parts[3]) if len(parts) > 3 else 1,
                    "budget": int(parts[4]) if len(parts) > 4 else 100,
                }
            except (ValueError, IndexError):
                pass # Not simple space-separated, continue to NLP parsing

        # Fallback to NLP-based parsing using a generative model
        print("Attempting NLP parsing...")
        prompt = f"""从以下用户输入中提取旅行信息，并以JSON格式返回。如果信息缺失，请使用默认值：
出发城市 (departure_city): 用户输入的第一个城市，如果未明确说明，则为空。
目的地 (destination): 用户输入的第二个城市，如果未明确说明，则为空。
出发日期 (departure_date): 格式为 YYYY-MM-DD，如果未明确说明，则为今天日期 ({datetime.date.today()})。
旅行天数 (duration): 整数，如果未明确说明，则为 1。
预算金额 (budget): 整数，如果未明确说明，则为 100。

用户输入: {user_input}

JSON格式示例:
{{"departure_city": "北京", "destination": "上海", "departure_date": "2025-08-01", "duration": 5, "budget": 5000}}
"""
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON string from model's response, handling potential markdown formatting
            json_string = response.text.strip()
            # Remove markdown code block fences if present
            if json_string.startswith('```json') and json_string.endswith('```'):
                json_string = json_string[7:-3].strip()
            elif json_string.startswith('```') and json_string.endswith('```'):
                json_string = json_string[3:-3].strip()

            # Clean up any extra characters before/after JSON
            json_string = re.sub(r'^.*?({.*}).*$', r'\1', json_string, flags=re.DOTALL)

            parsed_data = json.loads(json_string)

            # Apply default values if not provided by the model
            parsed_data.setdefault("departure_city", "")
            parsed_data.setdefault("destination", "")
            parsed_data.setdefault("departure_date", str(datetime.date.today()))
            parsed_data.setdefault("duration", 1)
            parsed_data.setdefault("budget", 100)

            return parsed_data
        except Exception as e:
            print(f"NLP parsing failed: {e}")
            # If all parsing fails, return a default empty structure or raise an error
            return {
                "departure_city": "",
                "destination": "",
                "departure_date": str(datetime.date.today()),
                "duration": 1,
                "budget": 100,
            }