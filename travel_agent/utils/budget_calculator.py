"""
Budget Calculator Utility
Handles budget calculations and optimizations for travel planning
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class BudgetCalculator:
    """Utility for budget calculations and optimizations."""
    
    def __init__(self):
        """Initialize the budget calculator."""
        # Default budget allocation percentages
        self.default_allocation = {
            'transportation': 0.30,  # 30%
            'accommodation': 0.35,   # 35%
            'dining': 0.20,          # 20%
            'activities': 0.15       # 15%
        }
        
        # Budget categories for detailed tracking
        self.categories = {
            'transportation': ['flights', 'trains', 'buses', 'local_transport', 'car_rental', 'fuel', 'parking'],
            'accommodation': ['hotels', 'hostels', 'vacation_rentals', 'resort_fees', 'taxes'],
            'dining': ['restaurants', 'street_food', 'groceries', 'drinks', 'tips'],
            'activities': ['attractions', 'tours', 'entertainment', 'shopping', 'experiences']
        }
        
        logger.info("Budget Calculator initialized")
    
    def calculate_budget_allocation(
        self,
        total_budget: float,
        duration: int,
        plan_type: str = 'balanced',
        custom_allocation: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate budget allocation across categories.
        
        Args:
            total_budget: Total available budget
            duration: Trip duration in days
            plan_type: Type of plan (economic, balanced, comfort, luxury)
            custom_allocation: Custom allocation percentages
            
        Returns:
            Dict containing detailed budget allocation
        """
        try:
            # Use custom allocation if provided, otherwise use plan-based allocation
            if custom_allocation:
                allocation_percentages = custom_allocation
            else:
                allocation_percentages = self._get_plan_allocation(plan_type)
            
            # Calculate amounts for each category
            allocation = {}
            daily_budget = total_budget / duration
            
            for category, percentage in allocation_percentages.items():
                category_budget = total_budget * percentage
                daily_category_budget = category_budget / duration
                
                allocation[category] = {
                    'total_amount': round(category_budget, 2),
                    'percentage': round(percentage * 100, 1),
                    'daily_amount': round(daily_category_budget, 2),
                    'subcategories': self._allocate_subcategory_budget(
                        category, category_budget, plan_type
                    )
                }
            
            # Add summary information
            allocation['summary'] = {
                'total_budget': total_budget,
                'daily_budget': round(daily_budget, 2),
                'duration': duration,
                'plan_type': plan_type,
                'currency': 'USD',  # Default currency
                'allocation_valid': self._validate_allocation(allocation_percentages)
            }
            
            logger.info(f"Budget allocation calculated for {plan_type} plan: ${total_budget}")
            return allocation
            
        except Exception as e:
            logger.error(f"Error calculating budget allocation: {str(e)}")
            return self._get_fallback_allocation(total_budget, duration)
    
    def _get_plan_allocation(self, plan_type: str) -> Dict[str, float]:
        """Get budget allocation percentages based on plan type."""
        allocations = {
            'economic': {
                'transportation': 0.32,  # More for transport
                'accommodation': 0.38,   # More for accommodation
                'dining': 0.18,          # Less for dining
                'activities': 0.12       # Less for activities
            },
            'balanced': {
                'transportation': 0.30,
                'accommodation': 0.35,
                'dining': 0.20,
                'activities': 0.15
            },
            'comfort': {
                'transportation': 0.28,  # Less for transport
                'accommodation': 0.32,   # Less for accommodation
                'dining': 0.22,          # More for dining
                'activities': 0.18       # More for activities
            },
            'luxury': {
                'transportation': 0.25,  # Less for transport
                'accommodation': 0.30,   # Less for accommodation
                'dining': 0.25,          # More for dining
                'activities': 0.20       # More for activities
            }
        }
        
        return allocations.get(plan_type, self.default_allocation)
    
    def _allocate_subcategory_budget(
        self,
        category: str,
        category_budget: float,
        plan_type: str
    ) -> Dict[str, float]:
        """Allocate budget within subcategories."""
        try:
            subcategories = self.categories.get(category, [])
            if not subcategories:
                return {}
            
            # Define subcategory allocation based on category and plan type
            subcategory_allocations = self._get_subcategory_allocations(category, plan_type)
            
            allocated_budget = {}
            for subcategory, percentage in subcategory_allocations.items():
                if subcategory in subcategories:
                    allocated_budget[subcategory] = round(category_budget * percentage, 2)
            
            return allocated_budget
            
        except Exception as e:
            logger.error(f"Error allocating subcategory budget: {str(e)}")
            return {}
    
    def _get_subcategory_allocations(self, category: str, plan_type: str) -> Dict[str, float]:
        """Get subcategory allocation percentages."""
        allocations = {
            'transportation': {
                'economic': {
                    'flights': 0.60, 'trains': 0.15, 'buses': 0.10,
                    'local_transport': 0.10, 'car_rental': 0.03, 'fuel': 0.02
                },
                'balanced': {
                    'flights': 0.65, 'trains': 0.10, 'buses': 0.05,
                    'local_transport': 0.12, 'car_rental': 0.05, 'fuel': 0.03
                },
                'comfort': {
                    'flights': 0.70, 'trains': 0.08, 'buses': 0.02,
                    'local_transport': 0.10, 'car_rental': 0.07, 'fuel': 0.03
                },
                'luxury': {
                    'flights': 0.75, 'trains': 0.05, 'buses': 0.00,
                    'local_transport': 0.08, 'car_rental': 0.10, 'fuel': 0.02
                }
            },
            'accommodation': {
                'economic': {
                    'hotels': 0.70, 'hostels': 0.20, 'vacation_rentals': 0.08, 'taxes': 0.02
                },
                'balanced': {
                    'hotels': 0.80, 'hostels': 0.05, 'vacation_rentals': 0.12, 'taxes': 0.03
                },
                'comfort': {
                    'hotels': 0.85, 'hostels': 0.00, 'vacation_rentals': 0.10, 'resort_fees': 0.02, 'taxes': 0.03
                },
                'luxury': {
                    'hotels': 0.90, 'vacation_rentals': 0.05, 'resort_fees': 0.03, 'taxes': 0.02
                }
            },
            'dining': {
                'economic': {
                    'restaurants': 0.40, 'street_food': 0.30, 'groceries': 0.25, 'drinks': 0.03, 'tips': 0.02
                },
                'balanced': {
                    'restaurants': 0.60, 'street_food': 0.20, 'groceries': 0.10, 'drinks': 0.05, 'tips': 0.05
                },
                'comfort': {
                    'restaurants': 0.75, 'street_food': 0.10, 'groceries': 0.05, 'drinks': 0.05, 'tips': 0.05
                },
                'luxury': {
                    'restaurants': 0.85, 'street_food': 0.05, 'groceries': 0.02, 'drinks': 0.05, 'tips': 0.03
                }
            },
            'activities': {
                'economic': {
                    'attractions': 0.50, 'tours': 0.20, 'entertainment': 0.15, 'shopping': 0.10, 'experiences': 0.05
                },
                'balanced': {
                    'attractions': 0.45, 'tours': 0.25, 'entertainment': 0.15, 'shopping': 0.10, 'experiences': 0.05
                },
                'comfort': {
                    'attractions': 0.40, 'tours': 0.30, 'entertainment': 0.15, 'shopping': 0.10, 'experiences': 0.05
                },
                'luxury': {
                    'attractions': 0.35, 'tours': 0.35, 'entertainment': 0.15, 'shopping': 0.10, 'experiences': 0.05
                }
            }
        }
        
        return allocations.get(category, {}).get(plan_type, {})
    
    def optimize_budget(
        self,
        current_allocation: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize budget allocation based on constraints.
        
        Args:
            current_allocation: Current budget allocation
            constraints: Budget constraints and preferences
            
        Returns:
            Optimized budget allocation
        """
        try:
            optimized_allocation = current_allocation.copy()
            total_budget = current_allocation['summary']['total_budget']
            
            # Apply constraints
            if 'max_accommodation' in constraints:
                max_accommodation = constraints['max_accommodation']
                current_accommodation = current_allocation['accommodation']['total_amount']
                
                if current_accommodation > max_accommodation:
                    # Reduce accommodation budget and redistribute
                    difference = current_accommodation - max_accommodation
                    optimized_allocation['accommodation']['total_amount'] = max_accommodation
                    
                    # Redistribute to other categories
                    self._redistribute_budget(optimized_allocation, difference, 'accommodation')
            
            if 'min_activities' in constraints:
                min_activities = constraints['min_activities']
                current_activities = current_allocation['activities']['total_amount']
                
                if current_activities < min_activities:
                    # Increase activities budget
                    difference = min_activities - current_activities
                    optimized_allocation['activities']['total_amount'] = min_activities
                    
                    # Reduce from other categories
                    self._reduce_budget(optimized_allocation, difference, 'activities')
            
            # Recalculate percentages
            self._recalculate_percentages(optimized_allocation, total_budget)
            
            logger.info("Budget optimization completed")
            return optimized_allocation
            
        except Exception as e:
            logger.error(f"Error optimizing budget: {str(e)}")
            return current_allocation
    
    def calculate_savings_opportunities(
        self,
        allocation: Dict[str, Any],
        destination: str
    ) -> List[Dict[str, Any]]:
        """
        Calculate potential savings opportunities.
        
        Args:
            allocation: Current budget allocation
            destination: Travel destination
            
        Returns:
            List of savings opportunities
        """
        try:
            opportunities = []
            
            # Transportation savings
            transport_budget = allocation.get('transportation', {}).get('total_amount', 0)
            if transport_budget > 500:
                opportunities.append({
                    'category': 'Transportation',
                    'opportunity': 'Book flights in advance',
                    'potential_savings': transport_budget * 0.15,
                    'description': 'Booking flights 6-8 weeks in advance can save 10-20%',
                    'difficulty': 'Easy'
                })
            
            # Accommodation savings
            accommodation_budget = allocation.get('accommodation', {}).get('total_amount', 0)
            if accommodation_budget > 300:
                opportunities.append({
                    'category': 'Accommodation',
                    'opportunity': 'Consider vacation rentals',
                    'potential_savings': accommodation_budget * 0.20,
                    'description': 'Vacation rentals can be 15-25% cheaper than hotels',
                    'difficulty': 'Medium'
                })
            
            # Dining savings
            dining_budget = allocation.get('dining', {}).get('total_amount', 0)
            if dining_budget > 200:
                opportunities.append({
                    'category': 'Dining',
                    'opportunity': 'Mix of restaurant and local food',
                    'potential_savings': dining_budget * 0.25,
                    'description': 'Eating at local places and markets can save 20-30%',
                    'difficulty': 'Easy'
                })
            
            # Activities savings
            activities_budget = allocation.get('activities', {}).get('total_amount', 0)
            if activities_budget > 150:
                opportunities.append({
                    'category': 'Activities',
                    'opportunity': 'City passes and group discounts',
                    'potential_savings': activities_budget * 0.18,
                    'description': 'City tourist passes and group bookings offer significant discounts',
                    'difficulty': 'Easy'
                })
            
            # Sort by potential savings
            opportunities.sort(key=lambda x: x['potential_savings'], reverse=True)
            
            logger.info(f"Found {len(opportunities)} savings opportunities")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error calculating savings opportunities: {str(e)}")
            return []
    
    def create_budget_summary(self, allocation: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive budget summary."""
        try:
            summary = allocation.get('summary', {})
            total_budget = summary.get('total_budget', 0)
            duration = summary.get('duration', 7)
            
            # Calculate totals
            category_totals = {}
            for category in ['transportation', 'accommodation', 'dining', 'activities']:
                category_data = allocation.get(category, {})
                category_totals[category] = category_data.get('total_amount', 0)
            
            # Create detailed summary
            budget_summary = {
                'overview': {
                    'total_budget': total_budget,
                    'daily_budget': round(total_budget / duration, 2),
                    'duration': duration,
                    'currency': 'USD'
                },
                'category_breakdown': category_totals,
                'daily_breakdown': {
                    category: round(amount / duration, 2)
                    for category, amount in category_totals.items()
                },
                'budget_health': self._assess_budget_health(allocation),
                'recommendations': self._generate_budget_recommendations(allocation)
            }
            
            return budget_summary
            
        except Exception as e:
            logger.error(f"Error creating budget summary: {str(e)}")
            return {}
    
    def _redistribute_budget(self, allocation: Dict[str, Any], amount: float, exclude_category: str):
        """Redistribute budget amount across categories (excluding one)."""
        categories = ['transportation', 'accommodation', 'dining', 'activities']
        categories.remove(exclude_category)
        
        per_category_increase = amount / len(categories)
        
        for category in categories:
            if category in allocation:
                allocation[category]['total_amount'] += per_category_increase
    
    def _reduce_budget(self, allocation: Dict[str, Any], amount: float, exclude_category: str):
        """Reduce budget amount from categories (excluding one)."""
        categories = ['transportation', 'accommodation', 'dining', 'activities']
        categories.remove(exclude_category)
        
        per_category_reduction = amount / len(categories)
        
        for category in categories:
            if category in allocation:
                allocation[category]['total_amount'] = max(
                    0, allocation[category]['total_amount'] - per_category_reduction
                )
    
    def _recalculate_percentages(self, allocation: Dict[str, Any], total_budget: float):
        """Recalculate percentages after budget changes."""
        for category in ['transportation', 'accommodation', 'dining', 'activities']:
            if category in allocation:
                amount = allocation[category]['total_amount']
                allocation[category]['percentage'] = round((amount / total_budget) * 100, 1)
    
    def _validate_allocation(self, allocation_percentages: Dict[str, float]) -> bool:
        """Validate that allocation percentages sum to 1.0."""
        total_percentage = sum(allocation_percentages.values())
        return abs(total_percentage - 1.0) < 0.01  # Allow small floating point errors
    
    def _assess_budget_health(self, allocation: Dict[str, Any]) -> str:
        """Assess the health of the budget allocation."""
        try:
            summary = allocation.get('summary', {})
            daily_budget = summary.get('daily_budget', 0)
            
            if daily_budget < 50:
                return 'Tight - Very careful planning required'
            elif daily_budget < 100:
                return 'Moderate - Good planning needed'
            elif daily_budget < 200:
                return 'Comfortable - Good flexibility'
            else:
                return 'Generous - Excellent flexibility'
                
        except Exception:
            return 'Unknown'
    
    def _generate_budget_recommendations(self, allocation: Dict[str, Any]) -> List[str]:
        """Generate budget recommendations."""
        recommendations = []
        
        try:
            # Check accommodation percentage
            accommodation_pct = allocation.get('accommodation', {}).get('percentage', 0)
            if accommodation_pct > 40:
                recommendations.append('Consider reducing accommodation costs - currently over 40% of budget')
            
            # Check activities percentage
            activities_pct = allocation.get('activities', {}).get('percentage', 0)
            if activities_pct < 10:
                recommendations.append('Consider allocating more budget for activities and experiences')
            
            # Check transportation percentage
            transport_pct = allocation.get('transportation', {}).get('percentage', 0)
            if transport_pct > 35:
                recommendations.append('Transportation costs are high - look for alternative options')
            
            # General recommendations
            recommendations.extend([
                'Track expenses daily to stay within budget',
                'Keep 10-15% buffer for unexpected expenses',
                'Research free activities and attractions at destination'
            ])
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
        
        return recommendations
    
    def _get_fallback_allocation(self, total_budget: float, duration: int) -> Dict[str, Any]:
        """Get fallback allocation when calculation fails."""
        return {
            'transportation': {'total_amount': total_budget * 0.30, 'percentage': 30.0},
            'accommodation': {'total_amount': total_budget * 0.35, 'percentage': 35.0},
            'dining': {'total_amount': total_budget * 0.20, 'percentage': 20.0},
            'activities': {'total_amount': total_budget * 0.15, 'percentage': 15.0},
            'summary': {
                'total_budget': total_budget,
                'daily_budget': total_budget / duration,
                'duration': duration,
                'plan_type': 'balanced',
                'currency': 'USD'
            }
        }
