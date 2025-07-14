from jinja2 import Environment, FileSystemLoader
from typing import Dict

class HTMLGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader('travel_agent/templates'))

    def generate_html(self, travel_plans: Dict, travel_info: Dict) -> str:
        """Generates an HTML travel plan from a dictionary of plans."""
        template = self.env.get_template('travel_plan.html')
        return template.render(plans=travel_plans, info=travel_info)
