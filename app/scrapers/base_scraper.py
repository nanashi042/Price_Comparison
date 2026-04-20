import requests
from abc import ABC, abstractmethod
from app.utils.error_handler import handle_scraper_error, ScraperException
from app.utils.scraper_utils import get_random_user_agent
from config.config import Config
from typing import Dict, Optional

class BaseScraper(ABC):
    """Base scraper class for all e-commerce sites"""
    
    def __init__(self):
        self.timeout = Config.SCRAPER_TIMEOUT
        self.max_retries = Config.MAX_RETRIES
        self.session = requests.Session()
        self.site_name = self.__class__.__name__
    
    def fetch_page(self, url: str) -> str:
        """
        Fetch HTML content from URL with retries
        """
        headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-IN,en;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise ScraperException(f"Failed to fetch {url}: {str(e)}")
                continue

        raise ScraperException(f"Failed to fetch {url}: exhausted retries")
    
    @abstractmethod
    def search(self, product_name: str) -> str:
        """
        Search for product on the e-commerce site
        Must be implemented by subclasses
        """
        raise NotImplementedError
    
    @abstractmethod
    def parse_results(self, html: str) -> Dict[str, Optional[object]]:
        """
        Parse HTML and extract price and URL
        Must be implemented by subclasses
        """
        raise NotImplementedError
    
    def execute_search(self, product_name: str) -> Dict[str, Optional[object]]:
        """
        Execute the search workflow
        """
        try:
            url = self.search(product_name)
            html = self.fetch_page(url)
            result = self.parse_results(html)
            return result
        except ScraperException as e:
            return handle_scraper_error(e, self.site_name)
        except Exception as e:
            return handle_scraper_error(e, self.site_name)
