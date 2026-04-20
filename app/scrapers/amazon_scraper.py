from app.scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
from app.utils.scraper_utils import clean_price
from urllib.parse import quote
from app.utils.error_handler import handle_scraper_error

class AmazonScraper(BaseScraper):
    """Amazon product scraper"""
    
    def __init__(self):
        super().__init__()
        self.site_name = 'amazon'
        self.base_url = 'https://www.amazon.in/s'
    
    def search(self, product_name):
        """Generate Amazon search URL"""
        return f"{self.base_url}?k={quote(product_name)}"
    
    def parse_results(self, html):
        """
        Parse Amazon search results
        Note: This is a basic implementation. Amazon has anti-scraping measures.
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        products = soup.find_all('div', {'data-component-type': 's-search-result'})
        price = None
        url = None

        for product in products:
            price_tag = product.select_one('span.a-price > span.a-offscreen') or product.find('span', {'class': 'a-price-whole'})
            parsed_price = clean_price(price_tag.get_text(strip=True)) if price_tag else None

            link_tag = product.select_one('a.a-link-normal.s-no-outline') or product.select_one('h2 a.a-link-normal')
            href = link_tag.get('href') if link_tag else None
            parsed_url = f"https://www.amazon.in{href}" if href and href.startswith('/') else href

            if parsed_price:
                price = parsed_price
                url = parsed_url
                break

        return {
            'site': self.site_name,
            'price': price,
            'url': url
        }

    def execute_product_url(self, product_url):
        """Extract price directly from an Amazon product page URL."""
        try:
            html = self.fetch_page(product_url)
            soup = BeautifulSoup(html, 'html.parser')

            title_tag = (
                soup.select_one('meta[property="og:title"]')
                or soup.select_one('meta[name="title"]')
                or soup.find('title')
            )
            name = None
            if title_tag:
                name = title_tag.get('content') if hasattr(title_tag, 'get') else title_tag.get_text(strip=True)
                if name:
                    name = name.split(':')[0].strip()

            price_tag = (
                soup.select_one('#corePrice_feature_div span.a-price span.a-offscreen')
                or soup.select_one('#corePriceDisplay_desktop_feature_div span.a-offscreen')
                or soup.select_one('span.a-price span.a-offscreen')
                or soup.select_one('span.a-price.aok-align-center .a-offscreen')
                or soup.select_one('span#priceblock_ourprice')
                or soup.select_one('span#priceblock_dealprice')
                or soup.select_one('meta[property="product:price:amount"]')
            )
            if price_tag and hasattr(price_tag, 'get') and price_tag.get('content'):
                price = clean_price(price_tag.get('content'))
            else:
                price = clean_price(price_tag.get_text(strip=True)) if price_tag else None

            canonical_tag = soup.select_one('link[rel="canonical"]')
            canonical_url = canonical_tag.get('href') if canonical_tag else None

            return {
                'site': self.site_name,
                'price': price,
                'url': canonical_url or product_url,
                'name': name
            }
        except Exception as error:
            return handle_scraper_error(error, self.site_name)
