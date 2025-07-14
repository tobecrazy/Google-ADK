from jinja2 import Environment, FileSystemLoader
from typing import Dict, List

class HTMLGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader('travel_agent/templates'))

    def generate_html(self, travel_plan: Dict) -> str:
        """Generates an HTML travel plan from a dictionary."""
        template = self.env.get_template('travel_plan.html')
        return template.render(travel_plan)