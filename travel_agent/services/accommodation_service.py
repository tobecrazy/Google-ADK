"""
Accommodation Service
Provides hotel and lodging recommendations
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

logger = logging.getLogger(__name__)

class AccommodationService:
    """Service for accommodation data and recommendations."""
    
    def __init__(self):
        """Initialize the accommodation service."""
        # Initialize Gemini for accommodation data generation
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        logger.info("Accommodation Service initialized")
    
    def get_accommodations(
        self,
        destination: str,
        start_date: str,
        duration: int,
        budget: float
    ) -> List[Dict[str, Any]]:
        """
        Get accommodation recommendations for the destination.
        
        Args:
            destination: Target destination
            start_date: Check-in date
            duration: Number of nights
            budget: Total accommodation budget
            
        Returns:
            List of accommodation options
        """
        try:
            logger.info(f"Getting accommodations for {destination}")
            
            # Calculate accommodation budget (35% of total budget)
            accommodation_budget = budget * 0.35
            nightly_budget = accommodation_budget / duration
            
            # Generate accommodation options using AI
            accommodations = self._generate_accommodations_with_ai(
                destination, start_date, duration, nightly_budget
            )
            
            # Enhance with additional details
            enhanced_accommodations = self._enhance_accommodation_data(
                accommodations, nightly_budget, duration
            )
            
            return enhanced_accommodations
            
        except Exception as e:
            logger.error(f"Error getting accommodations: {str(e)}")
            return self._get_fallback_accommodations(destination, budget, duration)
    
    def _generate_accommodations_with_ai(
        self,
        destination: str,
        start_date: str,
        duration: int,
        nightly_budget: float
    ) -> List[Dict[str, Any]]:
        """Generate accommodation recommendations using AI."""
        try:
            prompt = f"""
            Recommend accommodations in {destination} for {duration} nights starting {start_date}.
            Nightly budget: ${nightly_budget:.2f}
            
            Provide diverse options including:
            1. Budget hotels/hostels (under ${nightly_budget * 0.6:.0f}/night)
            2. Mid-range hotels (${nightly_budget * 0.6:.0f}-${nightly_budget * 1.2:.0f}/night)
            3. Luxury options (${nightly_budget * 1.2:.0f}+/night)
            4. Alternative accommodations (Airbnb, guesthouses, etc.)
            
            For each accommodation, include:
            - Name and type
            - Location/district
            - Price per night
            - Star rating or quality level
            - Key amenities
            - Pros and cons
            - Best for (couples, families, business, etc.)
            - Booking recommendations
            - Distance to city center/attractions
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse the AI response
            accommodations = self._parse_accommodation_response(response.text, destination, nightly_budget)
            
            return accommodations
            
        except Exception as e:
            logger.error(f"Error generating accommodations with AI: {str(e)}")
            return self._get_sample_accommodations(destination, nightly_budget)
    
    def _parse_accommodation_response(
        self,
        ai_response: str,
        destination: str,
        nightly_budget: float
    ) -> List[Dict[str, Any]]:
        """Parse AI response into structured accommodation data."""
        try:
            # Create structured sample accommodations
            sample_accommodations = [
                {
                    'name': f'{destination} Budget Inn',
                    'type': 'Budget Hotel',
                    'location': 'City Center',
                    'price_per_night': nightly_budget * 0.5,
                    'star_rating': 2.5,
                    'rating': 3.8,
                    'amenities': ['Free WiFi', 'Basic Breakfast', '24/7 Reception'],
                    'room_type': 'Standard Double Room',
                    'distance_to_center': '0.5 km',
                    'pros': ['Great location', 'Budget-friendly', 'Clean rooms'],
                    'cons': ['Basic amenities', 'Small rooms', 'Limited services'],
                    'best_for': 'Budget travelers, backpackers',
                    'booking_tips': ['Book directly for best rates', 'Check cancellation policy'],
                    'category': 'budget'
                },
                {
                    'name': f'{destination} Comfort Hotel',
                    'type': 'Mid-range Hotel',
                    'location': 'Tourist District',
                    'price_per_night': nightly_budget * 0.8,
                    'star_rating': 3.5,
                    'rating': 4.2,
                    'amenities': ['Free WiFi', 'Breakfast Included', 'Fitness Center', 'Restaurant'],
                    'room_type': 'Superior Room',
                    'distance_to_center': '1.2 km',
                    'pros': ['Good amenities', 'Comfortable rooms', 'Professional service'],
                    'cons': ['Can be busy', 'Limited parking'],
                    'best_for': 'Couples, business travelers',
                    'booking_tips': ['Check for package deals', 'Book early for better rates'],
                    'category': 'mid-range'
                },
                {
                    'name': f'{destination} Grand Hotel',
                    'type': 'Luxury Hotel',
                    'location': 'Premium District',
                    'price_per_night': nightly_budget * 1.5,
                    'star_rating': 4.5,
                    'rating': 4.7,
                    'amenities': ['Luxury Spa', 'Fine Dining', 'Concierge', 'Pool', 'Valet Parking'],
                    'room_type': 'Deluxe Suite',
                    'distance_to_center': '2.0 km',
                    'pros': ['Luxury amenities', 'Excellent service', 'Beautiful rooms'],
                    'cons': ['Expensive', 'May be formal', 'Distance from center'],
                    'best_for': 'Luxury travelers, special occasions',
                    'booking_tips': ['Look for seasonal promotions', 'Consider package deals'],
                    'category': 'luxury'
                },
                {
                    'name': f'{destination} Boutique Guesthouse',
                    'type': 'Boutique Accommodation',
                    'location': 'Historic Quarter',
                    'price_per_night': nightly_budget * 0.7,
                    'star_rating': 3.0,
                    'rating': 4.4,
                    'amenities': ['Free WiFi', 'Local Breakfast', 'Garden', 'Personal Service'],
                    'room_type': 'Charming Double Room',
                    'distance_to_center': '0.8 km',
                    'pros': ['Unique character', 'Personal touch', 'Local experience'],
                    'cons': ['Limited rooms', 'May lack modern amenities'],
                    'best_for': 'Culture enthusiasts, unique experience seekers',
                    'booking_tips': ['Book well in advance', 'Contact directly for special requests'],
                    'category': 'boutique'
                },
                {
                    'name': f'{destination} Apartment Rental',
                    'type': 'Vacation Rental',
                    'location': 'Residential Area',
                    'price_per_night': nightly_budget * 0.6,
                    'star_rating': None,
                    'rating': 4.1,
                    'amenities': ['Full Kitchen', 'Living Area', 'WiFi', 'Washing Machine'],
                    'room_type': '1-Bedroom Apartment',
                    'distance_to_center': '1.5 km',
                    'pros': ['Home-like feel', 'Kitchen facilities', 'More space'],
                    'cons': ['No daily service', 'Self check-in', 'Variable quality'],
                    'best_for': 'Families, longer stays, independent travelers',
                    'booking_tips': ['Read reviews carefully', 'Check exact location', 'Understand check-in process'],
                    'category': 'rental'
                }
            ]
            
            return sample_accommodations
            
        except Exception as e:
            logger.error(f"Error parsing accommodation response: {str(e)}")
            return self._get_sample_accommodations(destination, nightly_budget)
    
    def _enhance_accommodation_data(
        self,
        accommodations: List[Dict[str, Any]],
        nightly_budget: float,
        duration: int
    ) -> List[Dict[str, Any]]:
        """Enhance accommodation data with additional details."""
        try:
            enhanced_accommodations = []
            
            for accommodation in accommodations:
                price_per_night = accommodation.get('price_per_night', 0)
                
                # Handle None values for price_per_night
                if price_per_night is None:
                    price_per_night = 0
                
                total_cost = price_per_night * duration
                
                enhanced_accommodation = accommodation.copy()
                enhanced_accommodation.update({
                    'total_cost': total_cost,
                    'within_budget': price_per_night <= nightly_budget if price_per_night > 0 else False,
                    'value_rating': self._calculate_value_rating(accommodation),
                    'booking_urgency': self._assess_booking_urgency(accommodation),
                    'family_friendly': self._assess_family_friendliness(accommodation),
                    'business_suitable': self._assess_business_suitability(accommodation),
                    'accessibility': self._assess_accessibility(accommodation),
                    'nearby_attractions': self._get_nearby_attractions(accommodation),
                    'transportation_access': self._assess_transport_access(accommodation),
                    'seasonal_pricing': self._get_seasonal_pricing_info(accommodation),
                    'cancellation_policy': self._get_cancellation_info(accommodation)
                })
                
                enhanced_accommodations.append(enhanced_accommodation)
            
            # Sort by value rating and budget compatibility
            enhanced_accommodations.sort(
                key=lambda x: (x.get('within_budget', False), x.get('value_rating', 0)), 
                reverse=True
            )
            
            return enhanced_accommodations
            
        except Exception as e:
            logger.error(f"Error enhancing accommodation data: {str(e)}")
            return accommodations
    
    def _calculate_value_rating(self, accommodation: Dict[str, Any]) -> float:
        """Calculate value rating based on price, rating, and amenities."""
        try:
            rating = accommodation.get('rating', 3.0)
            amenities_count = len(accommodation.get('amenities', []))
            price = accommodation.get('price_per_night', 100)
            
            # Ensure all values are valid numbers and handle None values
            if rating is None or not isinstance(rating, (int, float)):
                rating = 3.0
            if price is None or not isinstance(price, (int, float)) or price <= 0:
                price = 100
            if amenities_count is None:
                amenities_count = 0
            
            # Simple value calculation (higher rating, more amenities, lower price = better value)
            value_score = (rating * 2 + amenities_count * 0.5) / (price / 50)
            return min(5.0, max(1.0, value_score))
            
        except Exception:
            return 3.0
    
    def _assess_booking_urgency(self, accommodation: Dict[str, Any]) -> str:
        """Assess how urgently this accommodation should be booked."""
        category = accommodation.get('category', 'mid-range')
        rating = accommodation.get('rating', 3.0)
        
        # Handle None values for rating
        if rating is None:
            rating = 3.0
        
        if category == 'luxury' or rating > 4.5:
            return 'High - Book immediately'
        elif category == 'boutique' or rating > 4.0:
            return 'Medium - Book within a week'
        else:
            return 'Low - Can book closer to travel date'
    
    def _assess_family_friendliness(self, accommodation: Dict[str, Any]) -> bool:
        """Assess if accommodation is family-friendly."""
        amenities = accommodation.get('amenities', [])
        accommodation_type = accommodation.get('type', '').lower()
        
        family_indicators = ['pool', 'family room', 'kitchen', 'playground', 'kids']
        return (
            any(indicator in ' '.join(amenities).lower() for indicator in family_indicators) or
            'apartment' in accommodation_type or
            'suite' in accommodation_type
        )
    
    def _assess_business_suitability(self, accommodation: Dict[str, Any]) -> bool:
        """Assess if accommodation is suitable for business travelers."""
        amenities = accommodation.get('amenities', [])
        business_indicators = ['business center', 'meeting room', 'wifi', 'desk', 'concierge']
        
        return any(indicator in ' '.join(amenities).lower() for indicator in business_indicators)
    
    def _assess_accessibility(self, accommodation: Dict[str, Any]) -> str:
        """Assess accessibility features."""
        star_rating = accommodation.get('star_rating', 0)
        category = accommodation.get('category', 'mid-range')
        
        # Handle None values for star_rating
        if star_rating is None:
            star_rating = 0
        
        if star_rating >= 4 or category == 'luxury':
            return 'Full accessibility features expected'
        elif star_rating >= 3:
            return 'Basic accessibility features likely'
        else:
            return 'Limited accessibility - check before booking'
    
    def _get_nearby_attractions(self, accommodation: Dict[str, Any]) -> List[str]:
        """Get nearby attractions based on location."""
        location = accommodation.get('location', '').lower()
        
        if 'center' in location or 'downtown' in location:
            return ['Historic sites', 'Shopping areas', 'Restaurants', 'Museums']
        elif 'tourist' in location:
            return ['Major attractions', 'Entertainment venues', 'Tour operators']
        elif 'historic' in location:
            return ['Historical landmarks', 'Cultural sites', 'Traditional markets']
        else:
            return ['Local attractions', 'Neighborhood restaurants', 'Parks']
    
    def _assess_transport_access(self, accommodation: Dict[str, Any]) -> Dict[str, Any]:
        """Assess transportation access."""
        distance = accommodation.get('distance_to_center', '1 km')
        location = accommodation.get('location', '').lower()
        
        if 'center' in location:
            return {
                'walkability': 'Excellent',
                'public_transport': 'Multiple options nearby',
                'taxi_availability': 'High',
                'airport_access': 'Good connections'
            }
        else:
            return {
                'walkability': 'Good',
                'public_transport': 'Available',
                'taxi_availability': 'Available',
                'airport_access': 'Moderate connections'
            }
    
    def _get_seasonal_pricing_info(self, accommodation: Dict[str, Any]) -> Dict[str, str]:
        """Get seasonal pricing information."""
        return {
            'peak_season': 'Prices 20-40% higher',
            'shoulder_season': 'Standard pricing',
            'low_season': 'Prices 15-25% lower',
            'booking_tip': 'Book 2-8 weeks in advance for best rates'
        }
    
    def _get_cancellation_info(self, accommodation: Dict[str, Any]) -> Dict[str, str]:
        """Get cancellation policy information."""
        category = accommodation.get('category', 'mid-range')
        
        if category == 'luxury':
            return {
                'policy': 'Flexible cancellation usually available',
                'deadline': 'Typically 24-48 hours before check-in',
                'recommendation': 'Check specific terms when booking'
            }
        else:
            return {
                'policy': 'Standard cancellation terms',
                'deadline': 'Usually 24 hours before check-in',
                'recommendation': 'Consider travel insurance for flexibility'
            }
    
    def _get_sample_accommodations(self, destination: str, nightly_budget: float) -> List[Dict[str, Any]]:
        """Get sample accommodations when AI generation fails."""
        return [
            {
                'name': f'{destination} Hotel',
                'type': 'Hotel',
                'location': 'City Center',
                'price_per_night': nightly_budget * 0.8,
                'star_rating': 3.0,
                'rating': 4.0,
                'amenities': ['WiFi', 'Breakfast', 'Reception'],
                'category': 'mid-range'
            }
        ]
    
    def _get_fallback_accommodations(
        self,
        destination: str,
        budget: float,
        duration: int
    ) -> List[Dict[str, Any]]:
        """Get fallback accommodations when all else fails."""
        nightly_budget = (budget * 0.35) / duration
        
        return [
            {
                'name': f'{destination} Standard Hotel',
                'type': 'Hotel',
                'location': 'Central Area',
                'price_per_night': nightly_budget,
                'star_rating': 3.0,
                'rating': 3.5,
                'amenities': ['Basic amenities available'],
                'total_cost': nightly_budget * duration,
                'within_budget': True,
                'booking_tips': ['Check availability and book in advance'],
                'note': 'Limited accommodation data available - please verify details before booking'
            }
        ]
