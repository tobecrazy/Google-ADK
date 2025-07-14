from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class InputHandler:
    """处理用户输入参数，设置默认值和进行基本验证。"""

    def process_input(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理用户输入的旅行信息，并填充默认值。
        Args:
            user_input: 包含旅行信息的字典。
        Returns:
            处理后的旅行信息字典。
        """
        processed_input = {
            "departure_city": user_input.get("departure_city"),
            "destination": user_input.get("destination"),
            "departure_date": self._get_departure_date(user_input.get("departure_date")),
            "duration": int(user_input.get("duration", 1)),
            "budget": float(user_input.get("budget", 100.0))
        }

        # 基本验证
        if not processed_input["departure_city"]:
            raise ValueError("出发城市是必填项。")
        if not processed_input["destination"]:
            raise ValueError("旅行目的地是必填项。")
        if processed_input["duration"] <= 0:
            raise ValueError("旅行天数必须大于0。")
        if processed_input["budget"] <= 0:
            raise ValueError("预算金额必须大于0。")

        return processed_input

    def _get_departure_date(self, date_str: Optional[str]) -> str:
        """
        获取出发日期，如果未提供则使用当前系统日期。
        Args:
            date_str: 用户提供的日期字符串。
        Returns:
            格式化后的日期字符串 (YYYY-MM-DD)。
        """
        if date_str:
            try:
                # 尝试解析用户提供的日期
                datetime.strptime(date_str, "%Y-%m-%d")
                return date_str
            except ValueError:
                raise ValueError("出发日期格式不正确，应为 YYYY-MM-DD。")
        else:
            # 默认使用当前系统日期
            return datetime.now().strftime("%Y-%m-%d")