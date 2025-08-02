"""
Restaurant Data Aggregator
Combines restaurant data from multiple sources with intelligent deduplication and ranking
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import json
import hashlib
from collections import defaultdict

# Add the parent directory to sys.path to enable absolute imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from travel_agent.utils.restaurant_scraper import RestaurantScraper

logger = logging.getLogger(__name__)

class RestaurantDataAggregator:
    """Aggregates restaurant data from multiple sources with intelligent processing."""
    
    def __init__(self):
        """Initialize the restaurant data aggregator."""
        # NOTE: Google ADK automatically provides MCP tools to the LLM agent
        # The LLM agent can call MCP tools directly without a wrapper function
        self.web_scraper = RestaurantScraper()
        
        # Cache for storing recent results
        self.cache = {}
        self.cache_duration = timedelta(hours=6)  # Cache for 6 hours
        
        # Data source weights for ranking
        self.source_weights = {
            'amap': 1.0,           # Highest weight for real API data
            'tripadvisor': 0.9,    # High weight for established review platform
            'tourism_site': 0.8,   # Good weight for official tourism data
            'food_blog': 0.7,      # Medium weight for curated content
            'search_engine': 0.6,  # Lower weight for generic search results
            'ai_fallback': 0.3     # Lowest weight for AI-generated content
        }
        
        logger.info("Restaurant Data Aggregator initialized (Google ADK handles MCP integration automatically)")
    
    def get_comprehensive_restaurant_data(
        self,
        destination: str,
        budget: float,
        location_coords: Optional[str] = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get comprehensive restaurant data from all available sources.
        
        Args:
            destination: Target destination
            budget: Daily food budget
            location_coords: Optional coordinates in "longitude,latitude" format
            max_results: Maximum number of results to return
            
        Returns:
            List of comprehensive restaurant recommendations
        """
        try:
            logger.info(f"Getting comprehensive restaurant data for {destination}")
            
            # Check cache first
            cache_key = self._generate_cache_key(destination, budget, location_coords)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                logger.info(f"Returning cached restaurant data for {destination}")
                return cached_result[:max_results]
            
            all_restaurants = []
            
            # Source 1: Amap API data (highest priority)
            amap_restaurants = self._get_amap_restaurants(destination, budget, location_coords)
            all_restaurants.extend(amap_restaurants)
            logger.info(f"Retrieved {len(amap_restaurants)} restaurants from Amap API")
            
            # Source 2: Web scraping from multiple sources
            scraped_restaurants = self._get_scraped_restaurants(destination, max_results)
            all_restaurants.extend(scraped_restaurants)
            logger.info(f"Retrieved {len(scraped_restaurants)} restaurants from web scraping")
            
            # Source 3: AI-generated fallback data
            if len(all_restaurants) < max_results // 2:
                ai_restaurants = self._get_ai_fallback_restaurants(destination, budget)
                all_restaurants.extend(ai_restaurants)
                logger.info(f"Added {len(ai_restaurants)} AI-generated restaurants as fallback")
            
            # Process and enhance the combined data
            processed_restaurants = self._process_combined_data(all_restaurants, destination, budget)
            
            # Cache the results
            self._cache_result(cache_key, processed_restaurants)
            
            # Return top results
            final_results = processed_restaurants[:max_results]
            logger.info(f"Returning {len(final_results)} comprehensive restaurant recommendations")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Error getting comprehensive restaurant data: {str(e)}")
            return self._get_emergency_fallback_restaurants(destination, budget, max_results)
    
    def _get_amap_restaurants(
        self,
        destination: str,
        budget: float,
        location_coords: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get restaurant data from Amap API."""
        try:
            # NOTE: Google ADK automatically provides MCP tools to the LLM agent
            # Since we can't directly call MCP tools from this service layer,
            # we'll skip Amap integration and rely on web scraping and AI fallback
            logger.info("Skipping Amap restaurants - Google ADK MCP tools are available to LLM agent only")
            return []
            
        except Exception as e:
            logger.error(f"Error getting Amap restaurants: {str(e)}")
            return []
    
    def _get_destination_coordinates(self, destination: str) -> Optional[str]:
        """Get coordinates for the destination using Amap geocoding."""
        # NOTE: Google ADK MCP tools are only available to the LLM agent
        # This service layer cannot directly call MCP tools
        logger.info("Skipping coordinate lookup - Google ADK MCP tools are available to LLM agent only")
        return None
    
    def _search_amap_by_location(self, location_coords: str, destination: str) -> List[Dict[str, Any]]:
        """Search Amap restaurants by location."""
        # NOTE: Google ADK MCP tools are only available to the LLM agent
        # This service layer cannot directly call MCP tools
        logger.info("Skipping Amap location search - Google ADK MCP tools are available to LLM agent only")
        return []
    
    def _search_amap_by_keywords(self, destination: str) -> List[Dict[str, Any]]:
        """Search Amap restaurants by keywords."""
        # NOTE: Google ADK MCP tools are only available to the LLM agent
        # This service layer cannot directly call MCP tools
        logger.info("Skipping Amap keyword search - Google ADK MCP tools are available to LLM agent only")
        return []
    
    def _parse_amap_poi(self, poi: Dict[str, Any], search_type: str) -> Optional[Dict[str, Any]]:
        """Parse Amap POI data into restaurant format."""
        try:
            if not poi or not isinstance(poi, dict):
                return None
            
            name = poi.get('name', '').strip()
            if not name or len(name) < 2:
                return None
            
            # Filter out non-restaurant POIs
            non_restaurant_keywords = [
                '银行', '医院', '学校', '酒店', '宾馆', '商场', 
                '超市', '加油站', '停车场', '地铁', '公交'
            ]
            
            if any(keyword in name for keyword in non_restaurant_keywords):
                return None
            
            restaurant = {
                'name': name,
                'amap_id': poi.get('id', ''),
                'address': poi.get('address', ''),
                'location': poi.get('location', ''),
                'type': poi.get('type', ''),
                'business_area': poi.get('business_area', ''),
                'cityname': poi.get('cityname', ''),
                'tel': poi.get('tel', ''),
                'distance': poi.get('distance', ''),
                'search_type': search_type,
                'retrieved_at': datetime.now().isoformat()
            }
            
            return restaurant
            
        except Exception as e:
            logger.warning(f"Error parsing Amap POI: {str(e)}")
            return None
    
    def _deduplicate_amap_restaurants(self, restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate Amap restaurants."""
        try:
            seen = set()
            unique_restaurants = []
            
            for restaurant in restaurants:
                amap_id = restaurant.get('amap_id', '')
                name = restaurant.get('name', '').strip().lower()
                location = restaurant.get('location', '').strip()
                
                # Use amap_id if available, otherwise use name + location
                if amap_id:
                    key = f"id:{amap_id}"
                else:
                    key = f"name:{name}:loc:{location}"
                
                if key not in seen:
                    seen.add(key)
                    unique_restaurants.append(restaurant)
            
            return unique_restaurants
            
        except Exception as e:
            logger.error(f"Error deduplicating Amap restaurants: {str(e)}")
            return restaurants
    
    def _get_scraped_restaurants(self, destination: str, max_results: int) -> List[Dict[str, Any]]:
        """Get restaurant data from web scraping."""
        try:
            scraped_restaurants = self.web_scraper.scrape_restaurants_multi_source(
                destination, max_results
            )
            
            # Mark source and add metadata
            for restaurant in scraped_restaurants:
                restaurant['data_source'] = 'web_scraping'
                restaurant['reliability_score'] = self.source_weights.get(
                    restaurant.get('source', 'search_engine'), 0.6
                )
            
            return scraped_restaurants
            
        except Exception as e:
            logger.error(f"Error getting scraped restaurants: {str(e)}")
            return []
    
    def _get_ai_fallback_restaurants(self, destination: str, budget: float) -> List[Dict[str, Any]]:
        """Get AI-generated fallback restaurants."""
        try:
            daily_food_budget = budget * 0.20 / 7
            
            fallback_restaurants = [
                {
                    'name': f'{destination}传统餐厅',
                    'description': f'{destination}当地传统餐厅，提供正宗的地方菜肴。',
                    'cuisine': 'Local Traditional',
                    'price_range': 'Mid-range',
                    'estimated_cost': daily_food_budget * 0.8,
                    'rating': 4.2,
                    'specialties': ['传统地方菜', '招牌菜'],
                    'location': destination,
                    'source': 'ai_fallback',
                    'data_source': 'ai_generated',
                    'reliability_score': 0.3
                },
                {
                    'name': f'{destination}小吃街',
                    'description': f'{destination}著名小吃聚集地，各种当地特色小吃。',
                    'cuisine': 'Street Food',
                    'price_range': 'Budget',
                    'estimated_cost': daily_food_budget * 0.4,
                    'rating': 4.0,
                    'specialties': ['当地小吃', '街头美食'],
                    'location': destination,
                    'source': 'ai_fallback',
                    'data_source': 'ai_generated',
                    'reliability_score': 0.3
                },
                {
                    'name': f'{destination}精品餐厅',
                    'description': f'{destination}高端餐厅，提供精致料理和优雅环境。',
                    'cuisine': 'Fine Dining',
                    'price_range': 'High-end',
                    'estimated_cost': daily_food_budget * 1.5,
                    'rating': 4.5,
                    'specialties': ['精致料理', '创意菜品'],
                    'location': destination,
                    'source': 'ai_fallback',
                    'data_source': 'ai_generated',
                    'reliability_score': 0.3
                }
            ]
            
            return fallback_restaurants
            
        except Exception as e:
            logger.error(f"Error generating AI fallback restaurants: {str(e)}")
            return []
    
    def _process_combined_data(
        self,
        all_restaurants: List[Dict[str, Any]],
        destination: str,
        budget: float
    ) -> List[Dict[str, Any]]:
        """Process and enhance combined restaurant data."""
        try:
            # Step 1: Advanced deduplication
            unique_restaurants = self._advanced_deduplication(all_restaurants)
            
            # Step 2: Data fusion for duplicates found across sources
            fused_restaurants = self._fuse_duplicate_data(unique_restaurants)
            
            # Step 3: Enhance with missing information
            enhanced_restaurants = self._enhance_missing_data(fused_restaurants, destination, budget)
            
            # Step 4: Calculate comprehensive scores
            scored_restaurants = self._calculate_comprehensive_scores(enhanced_restaurants)
            
            # Step 5: Sort by final score
            final_restaurants = sorted(
                scored_restaurants,
                key=lambda x: x.get('final_score', 0),
                reverse=True
            )
            
            logger.info(f"Processed {len(all_restaurants)} -> {len(final_restaurants)} restaurants")
            return final_restaurants
            
        except Exception as e:
            logger.error(f"Error processing combined {str(e)}")
            return all_restaurants
    
    def _advanced_deduplication(self, restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Advanced deduplication using multiple similarity metrics."""
        try:
            if not restaurants:
                return []
            
            # Group potentially similar restaurants
            similarity_groups = defaultdict(list)
            
            for restaurant in restaurants:
                # Create a normalized signature
                name = restaurant.get('name', '').strip().lower()
                clean_name = self._clean_restaurant_name(name)
                
                # Group by similar names
                signature = self._create_restaurant_signature(clean_name)
                similarity_groups[signature].append(restaurant)
            
            # Process each group
            unique_restaurants = []
            for group in similarity_groups.values():
                if len(group) == 1:
                    unique_restaurants.append(group[0])
                else:
                    # Find the best representative from the group
                    best_restaurant = self._select_best_from_group(group)
                    unique_restaurants.append(best_restaurant)
            
            logger.info(f"Advanced deduplication: {len(restaurants)} -> {len(unique_restaurants)}")
            return unique_restaurants
            
        except Exception as e:
            logger.error(f"Error in advanced deduplication: {str(e)}")
            return restaurants
    
    def _clean_restaurant_name(self, name: str) -> str:
        """Clean restaurant name for comparison."""
        import re
        
        # Remove common suffixes/prefixes
        name = re.sub(r'(餐厅|饭店|酒楼|restaurant|cafe|bar)$', '', name, flags=re.I)
        name = re.sub(r'^(老|新|大|小)', '', name)
        
        # Remove special characters and normalize spaces
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def _create_restaurant_signature(self, clean_name: str) -> str:
        """Create a signature for restaurant grouping."""
        # Use first few characters and length as signature
        if len(clean_name) < 3:
            return clean_name
        
        # Create signature based on first 3 characters and length category
        prefix = clean_name[:3]
        length_category = 'short' if len(clean_name) < 6 else 'medium' if len(clean_name) < 12 else 'long'
        
        return f"{prefix}_{length_category}"
    
    def _select_best_from_group(self, group: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the best restaurant from a group of similar ones."""
        try:
            # Score each restaurant in the group
            scored_restaurants = []
            
            for restaurant in group:
                score = 0
                
                # Source reliability
                source = restaurant.get('source', '')
                score += self.source_weights.get(source, 0.5) * 40
                
                # Data completeness
                fields = ['description', 'cuisine', 'price_range', 'specialties', 'rating']
                complete_fields = sum(1 for field in fields if restaurant.get(field))
                score += (complete_fields / len(fields)) * 30
                
                # Rating quality
                rating = restaurant.get('rating', 0)
                if rating > 0:
                    score += (rating / 5.0) * 20
                
                # Review count (if available)
                review_count = restaurant.get('review_count', 0)
                if review_count > 0:
                    score += min(review_count / 100, 1.0) * 10
                
                scored_restaurants.append((score, restaurant))
            
            # Return the highest scored restaurant
            best_restaurant = max(scored_restaurants, key=lambda x: x[0])[1]
            
            # Merge information from other restaurants in the group
            merged_restaurant = self._merge_restaurant_data(group, best_restaurant)
            
            return merged_restaurant
            
        except Exception as e:
            logger.error(f"Error selecting best from group: {str(e)}")
            return group[0]  # Return first as fallback
    
    def _merge_restaurant_data(self, group: List[Dict[str, Any]], base_restaurant: Dict[str, Any]) -> Dict[str, Any]:
        """Merge data from multiple restaurant entries."""
        try:
            merged = base_restaurant.copy()
            
            # Collect all specialties
            all_specialties = set(merged.get('specialties', []))
            for restaurant in group:
                specialties = restaurant.get('specialties', [])
                if isinstance(specialties, list):
                    all_specialties.update(specialties)
            
            merged['specialties'] = list(all_specialties)[:5]  # Limit to 5
            
            # Use the best description (longest meaningful one)
            best_description = merged.get('description', '')
            for restaurant in group:
                desc = restaurant.get('description', '')
                if len(desc) > len(best_description) and len(desc) < 300:
                    best_description = desc
            
            merged['description'] = best_description
            
            # Use highest rating
            best_rating = merged.get('rating', 0)
            for restaurant in group:
                rating = restaurant.get('rating', 0)
                if rating > best_rating:
                    best_rating = rating
            
            merged['rating'] = best_rating
            
            # Mark as merged data
            merged['data_sources'] = list(set(r.get('source', 'unknown') for r in group))
            merged['merged_from'] = len(group)
            
            return merged
            
        except Exception as e:
            logger.error(f"Error merging restaurant {str(e)}")
            return base_restaurant
    
    def _fuse_duplicate_data(self, restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fuse data from restaurants that might be duplicates across sources."""
        # This is already handled in _advanced_deduplication, so just return as-is
        return restaurants
    
    def _enhance_missing_data(
        self,
        restaurants: List[Dict[str, Any]],
        destination: str,
        budget: float
    ) -> List[Dict[str, Any]]:
        """Enhance restaurants with missing data."""
        try:
            daily_food_budget = budget * 0.20 / 7
            
            for restaurant in restaurants:
                # Ensure all required fields exist
                if not restaurant.get('description'):
                    restaurant['description'] = f"Popular restaurant in {destination}"
                
                if not restaurant.get('cuisine'):
                    restaurant['cuisine'] = 'Local'
                
                if not restaurant.get('price_range'):
                    restaurant['price_range'] = 'Mid-range'
                
                if not restaurant.get('rating'):
                    restaurant['rating'] = 4.0
                
                if not restaurant.get('specialties'):
                    cuisine = restaurant.get('cuisine', 'Local')
                    restaurant['specialties'] = [f"{cuisine} cuisine"]
                
                if not restaurant.get('estimated_cost'):
                    price_mapping = {
                        'Budget': daily_food_budget * 0.5,
                        'Mid-range': daily_food_budget * 0.8,
                        'High-end': daily_food_budget * 1.5,
                        'Luxury': daily_food_budget * 2.0
                    }
                    price_range = restaurant.get('price_range', 'Mid-range')
                    restaurant['estimated_cost'] = price_mapping.get(price_range, daily_food_budget)
                
                if not restaurant.get('location'):
                    restaurant['location'] = destination
                
                # Add budget compatibility
                cost = restaurant.get('estimated_cost', daily_food_budget)
                restaurant['budget_friendly'] = cost <= daily_food_budget * 1.2
                restaurant['cost_ratio'] = cost / daily_food_budget if daily_food_budget > 0 else 1.0
            
            return restaurants
            
        except Exception as e:
            logger.error(f"Error enhancing missing data: {str(e)}")
            return restaurants
    
    def _calculate_comprehensive_scores(self, restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate comprehensive scores for restaurants."""
        try:
            for restaurant in restaurants:
                score = 0.0
                
                # Source reliability (0-25 points)
                reliability = restaurant.get('reliability_score', 0.5)
                score += reliability * 25
                
                # Rating quality (0-20 points)
                rating = restaurant.get('rating', 0)
                if rating > 0:
                    score += (rating / 5.0) * 20
                
                # Data completeness (0-20 points)
                fields = ['description', 'cuisine', 'price_range', 'specialties', 'address', 'tel']
                complete_fields = sum(1 for field in fields if restaurant.get(field))
                score += (complete_fields / len(fields)) * 20
                
                # Budget compatibility (0-15 points)
                if restaurant.get('budget_friendly'):
                    score += 15
                elif restaurant.get('cost_ratio', 1.0) <= 1.5:
                    score += 10
                elif restaurant.get('cost_ratio', 1.0) <= 2.0:
                    score += 5
                
                # Review count bonus (0-10 points)
                review_count = restaurant.get('review_count', 0)
                if review_count > 0:
                    score += min(review_count / 100, 1.0) * 10
                
                # Quality indicators (0-10 points)
                quality_score = restaurant.get('quality_score', 0)
                if quality_score > 0:
                    score += (quality_score / 100) * 10
                
                restaurant['final_score'] = min(score, 100.0)
            
            return restaurants
            
        except Exception as e:
            logger.error(f"Error calculating comprehensive scores: {str(e)}")
            return restaurants
    
    def _generate_cache_key(self, destination: str, budget: float, location_coords: Optional[str]) -> str:
        """Generate cache key for restaurant data."""
        key_data = f"{destination}_{budget}_{location_coords or 'no_coords'}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached result if available and not expired."""
        try:
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if datetime.now() - timestamp < self.cache_duration:
                    return cached_data
                else:
                    # Remove expired cache
                    del self.cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.warning(f"Error getting cached result: {str(e)}")
            return None
    
    def _cache_result(self, cache_key: str, data: List[Dict[str, Any]]):
        """Cache the result with timestamp."""
        try:
            self.cache[cache_key] = (data, datetime.now())
            
            # Clean old cache entries (keep only last 10)
            if len(self.cache) > 10:
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
                del self.cache[oldest_key]
                
        except Exception as e:
            logger.warning(f"Error caching result: {str(e)}")
    
    def _get_emergency_fallback_restaurants(
        self,
        destination: str,
        budget: float,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Get emergency fallback restaurants when all else fails."""
        try:
            daily_food_budget = budget * 0.20 / 7
            
            emergency_restaurants = []
            
            # Generate basic restaurants
            restaurant_types = [
                ('传统餐厅', 'Local Traditional', 'Mid-range', 0.8),
                ('小吃街', 'Street Food', 'Budget', 0.4),
                ('咖啡厅', 'Cafe', 'Mid-range', 0.6),
                ('快餐店', 'Fast Food', 'Budget', 0.3),
                ('精品餐厅', 'Fine Dining', 'High-end', 1.5)
            ]
            
            for i, (name_suffix, cuisine, price_range, cost_multiplier) in enumerate(restaurant_types):
                if len(emergency_restaurants) >= max_results:
                    break
                
                restaurant = {
                    'name': f'{destination}{name_suffix}',
                    'description': f'{destination}当地{name_suffix}，提供{cuisine.lower()}风味。',
                    'cuisine': cuisine,
                    'price_range': price_range,
                    'estimated_cost': daily_food_budget * cost_multiplier,
                    'rating': 4.0 + (i * 0.1),
                    'specialties': [f'{cuisine} cuisine'],
                    'location': destination,
                    'source': 'emergency_fallback',
                    'data_source': 'emergency_generated',
                    'reliability_score': 0.1,
                    'final_score': 30.0 + (i * 5),
                    'budget_friendly': cost_multiplier <= 1.0
                }
                
                emergency_restaurants.append(restaurant)
            
            logger.warning(f"Using emergency fallback: generated {len(emergency_restaurants)} restaurants")
            return emergency_restaurants
            
        except Exception as e:
            logger.error(f"Error generating emergency fallback restaurants: {str(e)}")
            return []
    
    def close(self):
        """Close the aggregator and cleanup resources."""
        try:
            if self.web_scraper:
                self.web_scraper.close()
            
            # Clear cache
            self.cache.clear()
            
            logger.info("Restaurant Data Aggregator closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing restaurant aggregator: {str(e)}")
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.close()
