from app.scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
from app.utils.scraper_utils import clean_price
from urllib.parse import quote

class EbayScraper(BaseScraper):
    """eBay product scraper"""
    
    def __init__(self):
        super().__init__()
        self.site_name = 'ebay'
        self.base_url = 'https://www.ebay.com/sch/i.html'
    
    def search(self, product_name):
        """Generate eBay search URL"""
        return f"{self.base_url}?_nkw={quote(product_name)}"
    
    def parse_results(self, html):
        """
        Parse eBay search results
        Note: This is a basic implementation. eBay has anti-scraping measures.
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        products = soup.select('li.s-item') or soup.select('div.s-item')
        price = None
        url = None

        for product in products:
            price_tag = product.select_one('span.s-item__price')
            parsed_price = clean_price(price_tag.get_text(strip=True)) if price_tag else None

            link_tag = product.select_one('a.s-item__link')
            parsed_url = link_tag.get('href') if link_tag else None

            if parsed_price:
                price = parsed_price
                url = parsed_url
                break

        return {
            'site': self.site_name,
            'price': price,
            'url': url
        }
