import re

def clean_price(price_str):
    """
    Extract numeric price from string
    Handles formats like $99.99, ₹999, etc.
    """
    if price_str is None:
        return None
    
    text = str(price_str).strip()

    # Extract the first plausible numeric token (supports 12,999.50 and 12999)
    match = re.search(r'\d[\d,]*(?:\.\d+)?', text)
    if not match:
        return None

    cleaned = match.group(0).replace(',', '')
    try:
        return float(cleaned)
    except ValueError:
        return None

def validate_url(url):
    """Validate if URL is valid"""
    if url is None:
        return False
    
    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(url_pattern, url))

def get_random_user_agent():
    """Get a random user agent from the list"""
    import random
    from config.config import Config
    return random.choice(Config.USER_AGENTS)
