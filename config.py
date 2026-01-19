# config.py

# BINGHAMTON UNIVERSITY NEWS CONFIGURATION
BASE_URL = "https://www.binghamton.edu/news/home"
CSS_SELECTOR = "article, .story, .news-item"  # Target news story containers
REQUIRED_KEYS = [
    "story_title",
    "story_category",
    "story_summary",
    "story_url",
    "story_LinkedIn_post",
]

# TEST CONFIGURATION (commented out)
# BASE_URL = "http://quotes.toscrape.com"
# CSS_SELECTOR = "div.quote"
# REQUIRED_KEYS = ["name", "price"]

# ORIGINAL CONFIGURATION (commented out)
# BASE_URL = "https://www.theknot.com/marketplace/wedding-reception-venues-atlanta-ga"
# CSS_SELECTOR = "[class^='info-container']"
# REQUIRED_KEYS = ["name", "price", "location", "capacity", "rating", "reviews", "description"]
