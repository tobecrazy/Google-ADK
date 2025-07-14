from typing import Dict, List
from ..config.settings import BUDGET_ALLOCATION

class RoutePlanner:
    def plan_routes(self, travel_info: Dict, attractions: List[Dict]) -> Dict[str, List[Dict]]:
        """Plans multiple routes based on the travel information and attractions."""
        plans = {}
        budget = travel_info.get("budget", 100)

        # Economic Plan
        plans["economic"] = self._generate_plan("Economic", budget * 0.8, attractions)

        # Comfort Plan
        plans["comfort"] = self._generate_plan("Comfort", budget, attractions)

        # Luxury Plan
        plans["luxury"] = self._generate_plan("Luxury", budget * 1.5, attractions)

        return plans

    def _generate_plan(self, plan_type: str, budget: float, attractions: List[Dict]) -> List[Dict]:
        """Generates a single plan with a given budget."""
        # This is a simplified implementation. A real implementation would have more
        # sophisticated logic for cost estimation and activity selection.
        plan = []
        daily_budget = budget / 2 # Simplified daily budget
        for i, attraction in enumerate(attractions):
            if i < 2: # Limit to 2 attractions per day for simplicity
                plan.append({
                    "day": (i // 2) + 1,
                    "activity": f"{plan_type} visit to {attraction['name']}",
                    "description": attraction['description'],
                    "image_url": attraction['image_url']
                })
        return plan
