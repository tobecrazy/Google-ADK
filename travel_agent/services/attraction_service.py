"""
Attraction Service
Provides attraction and points of interest data
"""

import os
import logging
from typing import Dict, Any, List
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
from ..utils.image_handler import ImageHandler

logger = logging.getLogger(__name__)

class AttractionService:
    """Service for attraction and POI data."""
    
    def __init__(self):
        """Initialize the attraction service."""
        # Initialize Gemini for attraction data generation
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Initialize image handler for attraction images
        self.image_handler = ImageHandler()
        
        logger.info("Attraction Service initialized")
    
    def get_attractions(self, destination: str, budget: float) -> List[Dict[str, Any]]:
        """
        Get attractions and points of interest for a destination.
        
        Args:
            destination: Target destination
            budget: Total budget for activities
            
        Returns:
            List of attraction data
        """
        try:
            logger.info(f"Getting attractions for {destination}")
            
            # Use AI to generate comprehensive attraction data
            attractions_data = self._generate_attractions_with_ai(destination, budget)
            
            # Enhance with additional details
            enhanced_attractions = self._enhance_attraction_data(attractions_data, budget)
            
            # Add images to attractions
            attractions_with_images = self.image_handler.get_attraction_images(destination, enhanced_attractions)
            
            return attractions_with_images
            
        except Exception as e:
            logger.error(f"Error getting attractions: {str(e)}")
            return self._get_fallback_attractions(destination, budget)
    
    def _generate_attractions_with_ai(self, destination: str, budget: float) -> List[Dict[str, Any]]:
        """Use AI to generate attraction recommendations."""
        try:
            activities_budget = budget * 0.15  # 15% of total budget for activities
            
            prompt = f"""
            Generate a comprehensive list of attractions and activities for {destination}.
            Consider a total activities budget of ${activities_budget:.2f}.
            
            For each attraction, provide:
            1. Name
            2. Brief description (2-3 sentences)
            3. Category (Historical, Cultural, Natural, Entertainment, Religious, etc.)
            4. Estimated visit duration
            5. Approximate entrance fee (if any)
            6. Best time to visit
            7. Difficulty level (Easy, Moderate, Challenging)
            8. Age suitability
            9. Photography allowed (Yes/No/Restricted)
            10. Accessibility information
            
            Include a mix of:
            - Must-see famous attractions (5-7)
            - Hidden gems and local favorites (3-5)
            - Free or low-cost activities (3-4)
            - Cultural experiences (2-3)
            - Outdoor activities (2-3)
            - Family-friendly options (2-3)
            
            Provide 15-20 attractions total, covering different interests and budgets.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse the AI response into structured data
            attractions = self._parse_attractions_response(response.text, destination)
            
            return attractions
            
        except Exception as e:
            logger.error(f"Error generating attractions with AI: {str(e)}")
            return self._get_sample_attractions(destination)
    
    def _parse_attractions_response(self, ai_response: str, destination: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured attraction data."""
        try:
            # For now, create structured sample data
            # In a real implementation, this would parse the AI response more sophisticatedly
            
            sample_attractions = [
                {
                    'name': f'{destination} Historic Center',
                    'description': 'Explore the historic heart of the city with centuries-old architecture, charming streets, and cultural landmarks that tell the story of the region.',
                    'category': 'Historical',
                    'duration': '3-4 hours',
                    'entrance_fee': 0,
                    'best_time': 'Morning or late afternoon',
                    'difficulty': 'Easy',
                    'age_suitability': 'All ages',
                    'photography': 'Yes',
                    'accessibility': 'Mostly accessible',
                    'rating': 4.5,
                    'highlights': ['Historic architecture', 'Cultural sites', 'Walking tours'],
                    'search_keywords': [f'{destination} historic center', f'{destination} old town', f'{destination} architecture']
                },
                {
                    'name': f'{destination} Art Museum',
                    'description': 'World-class art collection featuring local and international artists, with rotating exhibitions and permanent galleries showcasing the region\'s cultural heritage.',
                    'category': 'Cultural',
                    'duration': '2-3 hours',
                    'entrance_fee': 15,
                    'best_time': 'Any time',
                    'difficulty': 'Easy',
                    'age_suitability': 'All ages',
                    'photography': 'Restricted',
                    'accessibility': 'Fully accessible',
                    'rating': 4.3,
                    'highlights': ['Art collections', 'Cultural exhibits', 'Educational tours'],
                    'search_keywords': [f'{destination} art museum', f'{destination} gallery', f'{destination} cultural center']
                },
                {
                    'name': f'{destination} Central Park',
                    'description': 'Beautiful urban park perfect for relaxation, picnics, and outdoor activities. Features gardens, walking paths, and recreational facilities.',
                    'category': 'Natural',
                    'duration': '2-4 hours',
                    'entrance_fee': 0,
                    'best_time': 'Morning or evening',
                    'difficulty': 'Easy',
                    'age_suitability': 'All ages',
                    'photography': 'Yes',
                    'accessibility': 'Mostly accessible',
                    'rating': 4.4,
                    'highlights': ['Nature walks', 'Picnic areas', 'Photography spots'],
                    'search_keywords': [f'{destination} park', f'{destination} garden', f'{destination} green space']
                },
                {
                    'name': f'{destination} Observatory Deck',
                    'description': 'Panoramic city views from the highest accessible point, offering breathtaking vistas especially during sunrise and sunset.',
                    'category': 'Entertainment',
                    'duration': '1-2 hours',
                    'entrance_fee': 25,
                    'best_time': 'Sunset or clear days',
                    'difficulty': 'Easy',
                    'age_suitability': 'All ages',
                    'photography': 'Yes',
                    'accessibility': 'Elevator access',
                    'rating': 4.6,
                    'highlights': ['City views', 'Photography', 'Sunset viewing'],
                    'search_keywords': [f'{destination} viewpoint', f'{destination} observatory', f'{destination} skyline']
                },
                {
                    'name': f'{destination} Local Market',
                    'description': 'Vibrant local market where you can experience authentic culture, taste local foods, and shop for unique souvenirs and crafts.',
                    'category': 'Cultural',
                    'duration': '2-3 hours',
                    'entrance_fee': 0,
                    'best_time': 'Morning',
                    'difficulty': 'Easy',
                    'age_suitability': 'All ages',
                    'photography': 'Yes',
                    'accessibility': 'Limited',
                    'rating': 4.2,
                    'highlights': ['Local culture', 'Food tasting', 'Shopping'],
                    'search_keywords': [f'{destination} market', f'{destination} bazaar', f'{destination} local shopping']
                },
                {
                    'name': f'{destination} Waterfront Promenade',
                    'description': 'Scenic waterfront area perfect for leisurely walks, dining, and enjoying water views. Popular spot for both locals and tourists.',
                    'category': 'Natural',
                    'duration': '1-3 hours',
                    'entrance_fee': 0,
                    'best_time': 'Evening',
                    'difficulty': 'Easy',
                    'age_suitability': 'All ages',
                    'photography': 'Yes',
                    'accessibility': 'Fully accessible',
                    'rating': 4.3,
                    'highlights': ['Water views', 'Walking paths', 'Dining options'],
                    'search_keywords': [f'{destination} waterfront', f'{destination} promenade', f'{destination} riverside']
                }
            ]
            
            # Try to extract more specific information from AI response if available
            if len(ai_response) > 200:
                # Add AI-generated content as additional context
                sample_attractions[0]['ai_description'] = ai_response[:300] + '...'
            
            return sample_attractions
            
        except Exception as e:
            logger.error(f"Error parsing attractions response: {str(e)}")
            return self._get_sample_attractions(destination)
    
    def _enhance_attraction_data(self, attractions: List[Dict[str, Any]], budget: float) -> List[Dict[str, Any]]:
        """Enhance attraction data with additional details."""
        try:
            activities_budget = budget * 0.15
            daily_activities_budget = activities_budget / 7  # Assuming 7 days
            
            enhanced_attractions = []
            
            for attraction in attractions:
                # Add budget-related information
                entrance_fee = attraction.get('entrance_fee', 0)
                
                enhanced_attraction = attraction.copy()
                enhanced_attraction.update({
                    'budget_friendly': entrance_fee <= daily_activities_budget * 0.5,
                    'premium_experience': entrance_fee > daily_activities_budget,
                    'estimated_total_cost': entrance_fee + (entrance_fee * 0.2),  # Include extras
                    'booking_required': entrance_fee > 20,  # Assume expensive attractions need booking
                    'group_discounts': entrance_fee > 10,  # Assume group discounts for paid attractions
                    'seasonal_availability': 'Year-round',  # Default, could be enhanced
                    'nearby_amenities': ['Restrooms', 'Parking', 'Food options'],
                    'tips': self._generate_attraction_tips(attraction)
                })
                
                enhanced_attractions.append(enhanced_attraction)
            
            # Sort by rating and budget-friendliness
            enhanced_attractions.sort(key=lambda x: (x.get('rating', 0), -x.get('entrance_fee', 0)), reverse=True)
            
            return enhanced_attractions
            
        except Exception as e:
            logger.error(f"Error enhancing attraction {str(e)}")
            return attractions
    
    def _generate_attraction_tips(self, attraction: Dict[str, Any]) -> List[str]:
        """Generate practical tips for visiting an attraction."""
        tips = []
        
        # General tips based on attraction properties
        if attraction.get('entrance_fee', 0) > 0:
            tips.append("Book tickets online in advance for potential discounts")
        
        if attraction.get('category') == 'Historical':
            tips.append("Consider hiring a local guide for deeper insights")
        
        if attraction.get('photography') == 'Restricted':
            tips.append("Check photography rules before your visit")
        
        if attraction.get('best_time') == 'Morning':
            tips.append("Arrive early to avoid crowds and enjoy cooler weather")
        
        if attraction.get('difficulty') == 'Challenging':
            tips.append("Wear comfortable shoes and bring water")
        
        # Add default tips if none generated
        if not tips:
            tips = [
                "Check opening hours before visiting",
                "Bring comfortable walking shoes",
                "Allow extra time for exploration"
            ]
        
        return tips[:3]  # Return top 3 tips
    
    def _get_sample_attractions(self, destination: str) -> List[Dict[str, Any]]:
        """Get sample attractions when AI generation fails."""
        return [
            {
                'name': f'{destination} Main Square',
                'description': 'Central square with historic significance and local atmosphere.',
                'category': 'Historical',
                'duration': '1-2 hours',
                'entrance_fee': 0,
                'rating': 4.2,
                'highlights': ['Historic architecture', 'Local culture']
            },
            {
                'name': f'{destination} Cultural Center',
                'description': 'Hub of local arts and cultural activities.',
                'category': 'Cultural',
                'duration': '2-3 hours',
                'entrance_fee': 10,
                'rating': 4.0,
                'highlights': ['Art exhibitions', 'Cultural events']
            },
            {
                'name': f'{destination} Scenic Viewpoint',
                'description': 'Beautiful views of the city and surrounding landscape.',
                'category': 'Natural',
                'duration': '1 hour',
                'entrance_fee': 5,
                'rating': 4.4,
                'highlights': ['Panoramic views', 'Photography']
            }
        ]
    
    def _get_fallback_attractions(self, destination: str, budget: float) -> List[Dict[str, Any]]:
        """Get fallback attractions when all else fails."""
        try:
            return [
                {
                    'name': f'{destination} City Tour',
                    'description': 'Comprehensive city tour covering major attractions and landmarks.',
                    'category': 'General',
                    'duration': '4-6 hours',
                    'entrance_fee': 30,
                    'best_time': 'Morning',
                    'difficulty': 'Easy',
                    'age_suitability': 'All ages',
                    'photography': 'Yes',
                    'accessibility': 'Varies by location',
                    'rating': 4.0,
                    'highlights': ['Overview of city', 'Multiple attractions', 'Guided experience'],
                    'budget_friendly': True,
                    'tips': ['Book in advance', 'Wear comfortable shoes', 'Bring camera']
                }
            ]
            
        except Exception as e:
            logger.error(f"Error creating fallback attractions: {str(e)}")
            return []
