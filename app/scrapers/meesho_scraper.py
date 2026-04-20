from app.scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
from app.utils.scraper_utils import clean_price
from app.utils.error_handler import handle_scraper_error
from urllib.parse import quote
import re


class MeeshoScraper(BaseScraper):
    """Meesho product scraper"""

    def __init__(self):
        super().__init__()
        self.site_name = 'meesho'
        self.base_url = 'https://www.meesho.com/search'
        self._last_query = ''

    def search(self, product_name):
        """Generate Meesho search URL"""
        self._last_query = product_name
        return f"{self.base_url}?q={quote(product_name)}"

    def parse_results(self, html):
        """Parse Meesho search results and extract first usable price/link."""
        soup = BeautifulSoup(html, 'html.parser')

        # Meesho markup changes often; use broad detection for INR-like prices.
        price_pattern = re.compile(r'(?:₹|Rs\.?|INR)\s*[\d,]+')
        candidates = soup.find_all(string=price_pattern)

        for text_node in candidates:
            price = clean_price(text_node)
            if price is None:
                continue

            parent = text_node.parent
            link_tag = parent.find_parent('a', href=True) if parent else None
            if not link_tag and parent:
                link_tag = parent.find('a', href=True)

            href = link_tag.get('href') if link_tag else None
            if href and href.startswith('/'):
                href = f"https://www.meesho.com{href}"

            return {
                'site': self.site_name,
                'price': price,
                'url': href
            }

        return {
            'site': self.site_name,
            'price': None,
            'url': self.search(self._last_query) if self._last_query else None
        }

    def execute_product_url(self, product_url):
        """Extract price directly from a Meesho product URL."""
        try:
            html = self.fetch_page(product_url)
            soup = BeautifulSoup(html, 'html.parser')

            price_tag = soup.find(string=re.compile(r'(?:₹|Rs\.?|INR)\s*[\d,]+'))
            price = clean_price(price_tag) if price_tag else None

            canonical_tag = soup.select_one('link[rel="canonical"]')
            canonical_url = canonical_tag.get('href') if canonical_tag else None

            return {
                'site': self.site_name,
                'price': price,
                'url': canonical_url or product_url
            }
        except Exception as error:
            return handle_scraper_error(error, self.site_name)
