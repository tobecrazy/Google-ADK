import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
USER_AGENTS = ["agent1", "agent2"]
REQUEST_INTERVAL = 1
BUDGET_ALLOCATION = {
    "transport": 0.3,
    "accommodation": 0.4,
    "dining": 0.2,
    "tickets": 0.1,
}

