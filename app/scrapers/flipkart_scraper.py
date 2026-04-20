from app.scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
from app.utils.scraper_utils import clean_price
from app.utils.error_handler import handle_scraper_error, ScraperException
from urllib.parse import quote
import json
import re

class FlipkartScraper(BaseScraper):
    """Flipkart product scraper"""
    
    def __init__(self):
        super().__init__()
        self.site_name = 'flipkart'
        self.base_url = 'https://www.flipkart.com/search'
        self._last_query = ''
    
    def search(self, product_name):
        """Generate Flipkart search URL"""
        self._last_query = product_name
        return f"{self.base_url}?q={quote(product_name)}"
    
    def parse_results(self, html):
        """
        Parse Flipkart search results
        Note: This is a basic implementation. Flipkart has anti-scraping measures.
        """
        if self._is_blocked_page(html):
            return {
                'site': self.site_name,
                'price': None,
                'url': None,
                'error': 'Flipkart returned a reCAPTCHA / blocked page'
            }

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

        if price is None:
            state_price, state_url = self._parse_from_initial_state(html)
            if state_price is not None:
                price = state_price
                url = state_url

        if url is None and self._last_query:
            url = self.search(self._last_query)

        return {
            'site': self.site_name,
            'price': price,
            'url': url
        }

    def _parse_from_initial_state(self, html):
        """Fallback parser for data embedded in Flipkart's window.__INITIAL_STATE__."""
        if self._is_blocked_page(html):
            return None, None

        match = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});\s*</script>', html, flags=re.S)
        if not match:
            return None, None

        try:
            state = json.loads(match.group(1))
        except json.JSONDecodeError:
            return None, None

        candidate = self._find_best_product_candidate(state)
        if not candidate:
            return None, None

        price = self._extract_candidate_price(candidate)
        url = self._extract_candidate_url(candidate)
        return price, url

    def _find_best_product_candidate(self, obj):
        candidates = []

        def walk(node):
            if isinstance(node, dict):
                pricing = node.get('pricing')
                title = node.get('title') or node.get('subTitle')
                if (
                    isinstance(pricing, dict)
                    and isinstance(pricing.get('finalPrice'), dict)
                    and pricing['finalPrice'].get('value') is not None
                    and isinstance(title, str)
                ):
                    candidates.append(node)

                for value in node.values():
                    walk(value)

            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(obj)
        if not candidates:
            return None

        query_tokens = {
            token.lower()
            for token in re.findall(r'[A-Za-z0-9]+', self._last_query or '')
            if len(token) > 2
        }

        def score(candidate):
            title = (candidate.get('title') or candidate.get('subTitle') or '').lower()
            title_tokens = set(re.findall(r'[A-Za-z0-9]+', title))
            overlap = len(query_tokens & title_tokens)
            return overlap

        best = max(candidates, key=score)
        if score(best) == 0:
            return candidates[0]
        return best

    def _extract_candidate_price(self, candidate):
        pricing = candidate.get('pricing')
        if not isinstance(pricing, dict):
            return None

        final_price = pricing.get('finalPrice')
        if isinstance(final_price, dict):
            value = final_price.get('value')
            if value is not None:
                return float(value)

        for key in ('sellingPrice', 'mrp'):
            section = pricing.get(key)
            if isinstance(section, dict) and section.get('value') is not None:
                return float(section['value'])

        return None

    def _extract_candidate_url(self, candidate):
        action = candidate.get('action')
        params = {}
        if isinstance(action, dict):
            raw_params = action.get('params')
            if isinstance(raw_params, dict):
                params = raw_params
            seo_url = params.get('seoUrl')
            if isinstance(seo_url, str) and seo_url:
                return f"https://www.flipkart.com{seo_url}" if seo_url.startswith('/') else seo_url

        base_info = candidate.get('productBaseInfoV1')
        product_attrs = {}
        if isinstance(base_info, dict):
            raw_product_attrs = base_info.get('productAttributes')
            if isinstance(raw_product_attrs, dict):
                product_attrs = raw_product_attrs
            url = product_attrs.get('url')
            if isinstance(url, str) and url:
                return f"https://www.flipkart.com{url}" if url.startswith('/') else url

        return None

    def _is_blocked_page(self, html):
        lowered = html.lower()
        return 'recaptcha' in lowered or 'flipkart reCAPTCHA'.lower() in lowered or 'robot' in lowered and 'verify' in lowered

    def execute_product_url(self, product_url):
        """Extract price directly from a Flipkart product page URL."""
        try:
            html = self.fetch_page(product_url)
            soup = BeautifulSoup(html, 'html.parser')

            price_tag = (
                soup.select_one('div.Nx9bqj')
                or soup.select_one('div._30jeq3')
                or soup.find(string=lambda t: bool(t) and '₹' in t)
            )
            if price_tag is not None and hasattr(price_tag, 'get_text'):
                price = clean_price(price_tag.get_text(strip=True))
            else:
                price = clean_price(price_tag)

            canonical_tag = soup.select_one('link[rel="canonical"]')
            canonical_url = canonical_tag.get('href') if canonical_tag else None

            return {
                'site': self.site_name,
                'price': price,
                'url': canonical_url or product_url
            }
        except Exception as error:
            return handle_scraper_error(error, self.site_name)

    def execute_search(self, product_name):
        """Run a Flipkart search and surface block reasons clearly."""
        try:
            url = self.search(product_name)
            html = self.fetch_page(url)
            return self.parse_results(html)
        except ScraperException as error:
            message = str(error)
            lowered = message.lower()
            if '403' in message or 'captcha' in lowered or 'forbidden' in lowered:
                return {
                    'site': self.site_name,
                    'price': None,
                    'url': None,
                    'error': 'Flipkart blocked the request with reCAPTCHA / 403'
                }
            return handle_scraper_error(error, self.site_name)
        except Exception as error:
            return handle_scraper_error(error, self.site_name)
