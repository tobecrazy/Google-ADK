# config/settings.py

# API Keys (replace with your actual keys or environment variables)
AMAP_API_KEY = "YOUR_AMAP_API_KEY"
OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"

# Crawling settings
REQUEST_INTERVAL = 2  # seconds between requests
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
]

# Budget allocation percentages
BUDGET_ALLOCATION = {
    "transportation": 0.30,
    "accommodation": 0.40,
    "dining": 0.20,
    "attractions": 0.10,
}

# Default values for planning
DEFAULT_DURATION = 1 # days
DEFAULT_BUDGET = 100 # CNY

# Image processing settings
IMAGE_MAX_WIDTH = 800
IMAGE_QUALITY = 85

# Data validation rules (example)
MIN_BUDGET = 50
MAX_DURATION = 30

# Weather related settings
WEATHER_FORECAST_DAYS = 15 # Max days for forecast
