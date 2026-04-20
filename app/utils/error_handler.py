import logging

logger = logging.getLogger(__name__)

class ScraperException(Exception):
    """Custom exception for scraper errors"""
    pass

def handle_scraper_error(error, site_name):
    """
    Handle scraper errors gracefully
    """
    logger.error(f"Error scraping {site_name}: {str(error)}")
    return {
        'site': site_name,
        'price': None,
        'url': None,
        'error': str(error)
    }
