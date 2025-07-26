"""
Date Parser Utility
Handles parsing of relative dates in Chinese and English
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class DateParser:
    """Utility class for parsing relative dates."""
    
    def __init__(self):
        """Initialize the date parser."""
        # Chinese relative date patterns
        self.chinese_patterns = {
            '今天': 0,
            '今日': 0,
            '明天': 1,
            '明日': 1,
            '后天': 2,
            '後天': 2,
            '大后天': 3,
            '大後天': 3,
            '昨天': -1,
            '昨日': -1,
            '前天': -2,
            '前日': -2
        }
        
        # English relative date patterns
        self.english_patterns = {
            'today': 0,
            'tomorrow': 1,
            'day after tomorrow': 2,
            'yesterday': -1,
            'day before yesterday': -2
        }
        
        # Number patterns in Chinese
        self.chinese_numbers = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
            '6': 6, '7': 7, '8': 8, '9': 9, '10': 10
        }
    
    def parse_relative_date(self, date_input: str, base_date: Optional[datetime] = None) -> str:
        """
        Parse relative date expressions and return YYYY-MM-DD format.
        
        Args:
            date_input: Date input string (could be relative or absolute)
            base_date: Base date for calculation (defaults to current date)
            
        Returns:
            Date string in YYYY-MM-DD format
        """
        try:
            if base_date is None:
                base_date = datetime.now()
            
            # Clean the input
            date_input = date_input.strip()
            
            # Check if it's already in YYYY-MM-DD format
            if re.match(r'^\d{4}-\d{2}-\d{2}$', date_input):
                return date_input
            
            # Check if it's in other standard formats
            standard_formats = [
                '%Y/%m/%d', '%Y.%m.%d', '%m/%d/%Y', '%m-%d-%Y',
                '%d/%m/%Y', '%d-%m-%Y', '%Y年%m月%d日'
            ]
            
            for fmt in standard_formats:
                try:
                    parsed_date = datetime.strptime(date_input, fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # Parse relative dates
            relative_days = self._parse_relative_expression(date_input)
            if relative_days is not None:
                target_date = base_date + timedelta(days=relative_days)
                return target_date.strftime('%Y-%m-%d')
            
            # If nothing matches, try to extract date from natural language
            extracted_date = self._extract_date_from_text(date_input, base_date)
            if extracted_date:
                return extracted_date
            
            # Fallback: return tomorrow's date
            logger.warning(f"Could not parse date '{date_input}', using tomorrow as fallback")
            tomorrow = base_date + timedelta(days=1)
            return tomorrow.strftime('%Y-%m-%d')
            
        except Exception as e:
            logger.error(f"Error parsing date '{date_input}': {str(e)}")
            # Return tomorrow as safe fallback
            tomorrow = (base_date or datetime.now()) + timedelta(days=1)
            return tomorrow.strftime('%Y-%m-%d')
    
    def _parse_relative_expression(self, text: str) -> Optional[int]:
        """Parse relative date expressions and return days offset."""
        try:
            text_lower = text.lower()
            
            # Check Chinese patterns
            for pattern, days in self.chinese_patterns.items():
                if pattern in text:
                    return days
            
            # Check English patterns
            for pattern, days in self.english_patterns.items():
                if pattern in text_lower:
                    return days
            
            # Check for patterns like "3天后", "5天前", "after 3 days", "in 2 days"
            chinese_future_pattern = r'(\d+|[一二三四五六七八九十])天后'
            chinese_past_pattern = r'(\d+|[一二三四五六七八九十])天前'
            english_future_pattern = r'(?:in|after)\s+(\d+)\s+days?'
            english_past_pattern = r'(\d+)\s+days?\s+ago'
            
            # Chinese future (X天后)
            match = re.search(chinese_future_pattern, text)
            if match:
                num_str = match.group(1)
                days = self._parse_chinese_number(num_str)
                if days:
                    return days
            
            # Chinese past (X天前)
            match = re.search(chinese_past_pattern, text)
            if match:
                num_str = match.group(1)
                days = self._parse_chinese_number(num_str)
                if days:
                    return -days
            
            # English future (in X days, after X days)
            match = re.search(english_future_pattern, text_lower)
            if match:
                return int(match.group(1))
            
            # English past (X days ago)
            match = re.search(english_past_pattern, text_lower)
            if match:
                return -int(match.group(1))
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing relative expression '{text}': {str(e)}")
            return None
    
    def _parse_chinese_number(self, num_str: str) -> Optional[int]:
        """Parse Chinese number string to integer."""
        try:
            # Try direct conversion first
            if num_str.isdigit():
                return int(num_str)
            
            # Check Chinese number mapping
            if num_str in self.chinese_numbers:
                return self.chinese_numbers[num_str]
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing Chinese number '{num_str}': {str(e)}")
            return None
    
    def _extract_date_from_text(self, text: str, base_date: datetime) -> Optional[str]:
        """Extract date from natural language text."""
        try:
            # Look for patterns like "下周一", "下个月", etc.
            # This is a simplified implementation
            
            if '下周' in text:
                # Next week - assume Monday
                days_until_next_monday = (7 - base_date.weekday()) % 7
                if days_until_next_monday == 0:
                    days_until_next_monday = 7
                target_date = base_date + timedelta(days=days_until_next_monday)
                return target_date.strftime('%Y-%m-%d')
            
            if '下个月' in text or '下月' in text:
                # Next month - assume first day
                if base_date.month == 12:
                    target_date = base_date.replace(year=base_date.year + 1, month=1, day=1)
                else:
                    target_date = base_date.replace(month=base_date.month + 1, day=1)
                return target_date.strftime('%Y-%m-%d')
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting date from text '{text}': {str(e)}")
            return None
    
    def get_current_date_info(self) -> Dict[str, str]:
        """Get current date information in various formats."""
        now = datetime.now()
        return {
            'current_date': now.strftime('%Y-%m-%d'),
            'current_datetime': now.strftime('%Y-%m-%d %H:%M:%S'),
            'today': now.strftime('%Y-%m-%d'),
            'tomorrow': (now + timedelta(days=1)).strftime('%Y-%m-%d'),
            'day_after_tomorrow': (now + timedelta(days=2)).strftime('%Y-%m-%d'),
            'current_year': str(now.year),
            'current_month': str(now.month),
            'current_day': str(now.day),
            'weekday': now.strftime('%A'),
            'weekday_chinese': self._get_chinese_weekday(now.weekday())
        }
    
    def _get_chinese_weekday(self, weekday: int) -> str:
        """Convert weekday number to Chinese."""
        chinese_weekdays = {
            0: '星期一', 1: '星期二', 2: '星期三', 3: '星期四',
            4: '星期五', 5: '星期六', 6: '星期日'
        }
        return chinese_weekdays.get(weekday, '未知')


# Global instance for easy access
date_parser = DateParser()


def parse_date(date_input: str, base_date: Optional[datetime] = None) -> str:
    """
    Convenience function to parse date input.
    
    Args:
        date_input: Date input string
        base_date: Base date for relative calculations
        
    Returns:
        Date string in YYYY-MM-DD format
    """
    return date_parser.parse_relative_date(date_input, base_date)


def get_current_date_info() -> Dict[str, str]:
    """Get current date information."""
    return date_parser.get_current_date_info()
