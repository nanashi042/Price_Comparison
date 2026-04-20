from app.scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
from app.utils.scraper_utils import clean_price
from urllib.parse import quote

class FlipkartScraper(BaseScraper):
    """Flipkart product scraper"""
    
    def __init__(self):
        super().__init__()
        self.site_name = 'flipkart'
        self.base_url = 'https://www.flipkart.com/search'
    
    def search(self, product_name):
        """Generate Flipkart search URL"""
        return f"{self.base_url}?q={quote(product_name)}"
    
    def parse_results(self, html):
        """
        Parse Flipkart search results
        Note: This is a basic implementation. Flipkart has anti-scraping measures.
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        products = soup.select('div._1AtVbE') or soup.select('div._2kHMtA')
        price = None
        url = None

        for product in products:
            price_tag = product.select_one('div._30jeq3') or product.select_one('div.Nx9bqj')
            parsed_price = clean_price(price_tag.get_text(strip=True)) if price_tag else None

            link_tag = product.select_one('a._1fQZEK') or product.select_one('a.CGtC98') or product.select_one('a[href*="/p/"]')
            href = link_tag.get('href') if link_tag else None
            parsed_url = f"https://www.flipkart.com{href}" if href and href.startswith('/') else href

            if parsed_price:
                price = parsed_price
                url = parsed_url
                break

        return {
            'site': self.site_name,
            'price': price,
            'url': url
        }
