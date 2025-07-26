"""
Dialect Service
Provides destination-specific dialect and local language phrases
"""

import os
import logging
from typing import Dict, Any, List
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

logger = logging.getLogger(__name__)

class DialectService:
    """Service for destination-specific dialect and local phrases."""
    
    def __init__(self):
        """Initialize the dialect service."""
        # Initialize Gemini for dialect generation
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Predefined dialect mappings for common Chinese destinations
        self.dialect_mappings = {
            "北京": {
                "hello": "您好嘞",
                "thank_you": "谢谢您嘞",
                "excuse_me": "不好意思哈",
                "how_much": "多少钱一个？",
                "very_good": "倍儿棒",
                "comfortable": "得劲儿",
                "walk_around": "溜达溜达",
                "look": "瞧瞧",
                "okay": "成",
                "please_help": "麻烦您"
            },
            "上海": {
                "hello": "侬好",
                "thank_you": "谢谢侬",
                "excuse_me": "对勿起",
                "how_much": "几钿钱？",
                "very_good": "老好额",
                "comfortable": "蛮好额",
                "walk_around": "兜兜",
                "look": "看看",
                "okay": "好额",
                "please_help": "帮帮忙"
            },
            "广州": {
                "hello": "你好",
                "thank_you": "唔该",
                "excuse_me": "唔好意思",
                "how_much": "几多钱？",
                "very_good": "好正",
                "comfortable": "好舒服",
                "walk_around": "行下",
                "look": "睇下",
                "okay": "得",
                "please_help": "帮下手"
            },
            "成都": {
                "hello": "你好哈",
                "thank_you": "谢谢哦",
                "excuse_me": "不好意思嘛",
                "how_much": "好多钱？",
                "very_good": "巴适得很",
                "comfortable": "安逸",
                "walk_around": "耍一哈",
                "look": "瞧一哈",
                "okay": "行",
                "please_help": "帮个忙嘛"
            },
            "西安": {
                "hello": "你好咧",
                "thank_you": "谢谢咧",
                "excuse_me": "不好意思咧",
                "how_much": "多少钱咧？",
                "very_good": "美得很",
                "comfortable": "舒坦",
                "walk_around": "转转",
                "look": "瞅瞅",
                "okay": "中",
                "please_help": "帮个忙"
            },
            "重庆": {
                "hello": "你好哈",
                "thank_you": "谢谢哦",
                "excuse_me": "不好意思嘛",
                "how_much": "好多钱嘛？",
                "very_good": "巴适得板",
                "comfortable": "安逸得很",
                "walk_around": "耍哈",
                "look": "看哈",
                "okay": "得行",
                "please_help": "帮哈忙"
            },
            "杭州": {
                "hello": "你好",
                "thank_you": "谢谢",
                "excuse_me": "对不起",
                "how_much": "多少钱？",
                "very_good": "蛮好的",
                "comfortable": "舒服",
                "walk_around": "走走",
                "look": "看看",
                "okay": "好的",
                "please_help": "帮个忙"
            },
            "南京": {
                "hello": "你好",
                "thank_you": "谢谢",
                "excuse_me": "不好意思",
                "how_much": "多少钱？",
                "very_good": "蛮好的",
                "comfortable": "舒服",
                "walk_around": "逛逛",
                "look": "看看",
                "okay": "好的",
                "please_help": "帮个忙"
            }
        }
        
        logger.info("Dialect Service initialized")
    
    def get_local_phrases(self, destination: str) -> List[str]:
        """
        Get local dialect phrases for a destination.
        
        Args:
            destination: Target destination
            
        Returns:
            List of local phrases
        """
        try:
            logger.info(f"Getting local phrases for {destination}")
            
            # Check if we have predefined dialect mapping
            if destination in self.dialect_mappings:
                dialect_map = self.dialect_mappings[destination]
                phrases = [
                    dialect_map.get("hello", "你好"),
                    dialect_map.get("thank_you", "谢谢"),
                    dialect_map.get("excuse_me", "不好意思"),
                    dialect_map.get("how_much", "多少钱？"),
                    dialect_map.get("very_good", "很好"),
                    dialect_map.get("comfortable", "舒服"),
                    dialect_map.get("walk_around", "走走"),
                    dialect_map.get("look", "看看")
                ]
                return phrases[:6]  # Return top 6 phrases
            
            # Use AI to generate dialect phrases for unknown destinations
            return self._generate_dialect_with_ai(destination)
            
        except Exception as e:
            logger.error(f"Error getting local phrases: {str(e)}")
            return self._get_fallback_phrases()
    
    def _generate_dialect_with_ai(self, destination: str) -> List[str]:
        """Use AI to generate dialect phrases for destinations."""
        try:
            prompt = f"""
            Generate 6-8 common local dialect phrases or expressions that tourists would find useful when visiting {destination}.
            
            Focus on:
            1. Local greeting
            2. Thank you expression
            3. Excuse me/Sorry
            4. How much does it cost?
            5. Very good/excellent
            6. Comfortable/nice
            7. Walk around/explore
            8. Look/see
            
            If {destination} is a Chinese city, provide the local dialect or regional variation.
            If it's an international destination, provide key phrases in the local language with Chinese pronunciation guide.
            
            Format: Return only the phrases, one per line, without explanations.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse the response into a list
            phrases = [phrase.strip() for phrase in response.text.split('\n') if phrase.strip()]
            
            # Filter and clean the phrases
            cleaned_phrases = []
            for phrase in phrases[:8]:  # Take first 8
                if phrase and len(phrase) < 50:  # Reasonable length
                    cleaned_phrases.append(phrase)
            
            return cleaned_phrases[:6] if cleaned_phrases else self._get_fallback_phrases()
            
        except Exception as e:
            logger.error(f"Error generating dialect with AI: {str(e)}")
            return self._get_fallback_phrases()
    
    def _get_fallback_phrases(self) -> List[str]:
        """Get fallback phrases when all else fails."""
        return [
            "你好",
            "谢谢",
            "不好意思",
            "多少钱？",
            "很好",
            "舒服"
        ]
    
    def get_cultural_etiquette(self, destination: str) -> List[str]:
        """
        Get cultural etiquette tips for a destination.
        
        Args:
            destination: Target destination
            
        Returns:
            List of cultural etiquette tips
        """
        try:
            # Use AI to generate destination-specific cultural etiquette
            prompt = f"""
            Generate 5-6 important cultural etiquette tips for tourists visiting {destination}.
            
            Focus on:
            1. Social interactions and greetings
            2. Dining etiquette
            3. Religious or cultural site behavior
            4. Tipping customs
            5. Dress code considerations
            6. Local customs to respect
            
            Make the tips practical and specific to {destination}.
            Format: Return only the tips, one per line, without numbering.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse the response into a list
            tips = [tip.strip() for tip in response.text.split('\n') if tip.strip()]
            
            # Clean and filter tips
            cleaned_tips = []
            for tip in tips[:6]:  # Take first 6
                if tip and len(tip) > 10 and len(tip) < 200:  # Reasonable length
                    cleaned_tips.append(tip)
            
            return cleaned_tips if cleaned_tips else self._get_fallback_etiquette()
            
        except Exception as e:
            logger.error(f"Error getting cultural etiquette: {str(e)}")
            return self._get_fallback_etiquette()
    
    def _get_fallback_etiquette(self) -> List[str]:
        """Get fallback cultural etiquette tips."""
        return [
            "尊重当地的传统习俗和文化",
            "在宗教场所保持庄重得体",
            "学习基本的当地语言问候语",
            "了解当地的用餐礼仪和习惯",
            "以友善和尊重的态度与当地人交流"
        ]
    
    def get_destination_specific_info(self, destination: str) -> Dict[str, Any]:
        """
        Get comprehensive destination-specific information.
        
        Args:
            destination: Target destination
            
        Returns:
            Dictionary with local phrases and cultural info
        """
        try:
            return {
                'local_phrases': self.get_local_phrases(destination),
                'cultural_etiquette': self.get_cultural_etiquette(destination),
                'dialect_available': destination in self.dialect_mappings
            }
            
        except Exception as e:
            logger.error(f"Error getting destination info: {str(e)}")
            return {
                'local_phrases': self._get_fallback_phrases(),
                'cultural_etiquette': self._get_fallback_etiquette(),
                'dialect_available': False
            }
