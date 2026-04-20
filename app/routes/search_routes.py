from flask import request, jsonify
from app.routes import search_bp
from app import db
from app.models import Product, PriceRecord, SearchHistory
from app.scrapers import AmazonScraper, FlipkartScraper, MeeshoScraper
from urllib.parse import urlparse, unquote
import re


def normalize_search_query(raw_query):
    """Convert pasted product URLs into a clean search query."""
    query = raw_query.strip()
    if query and not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', query) and re.match(r'^(www\.)?(amazon|flipkart|meesho)\.', query, flags=re.I):
        query = f'https://{query}'

    parsed = urlparse(query)

    if parsed.scheme in ('http', 'https') and parsed.netloc:
        netloc = parsed.netloc.lower()
        segments = [segment for segment in parsed.path.split('/') if segment]

        slug = ''
        if 'dp' in segments:
            dp_index = segments.index('dp')
            if dp_index > 0:
                slug = segments[dp_index - 1]

        if not slug and segments:
            slug = segments[-1]

        slug = unquote(slug)
        cleaned = slug.replace('-', ' ').replace('_', ' ')
        cleaned = re.sub(r'[^A-Za-z0-9 ]+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        source_site = None
        if 'amazon.' in netloc:
            source_site = 'amazon'
        elif 'flipkart.' in netloc:
            source_site = 'flipkart'
        elif 'meesho.' in netloc:
            source_site = 'meesho'

        return {
            'query': cleaned or query,
            'source_site': source_site,
            'source_url': query
        }

    return {
        'query': re.sub(r'\s+', ' ', query),
        'source_site': None,
        'source_url': None
    }

@search_bp.route('/product', methods=['GET'])
def search_product():
    """
    Search for a product across multiple e-commerce sites
    Query parameter: q (product name)
    """
    raw_query = request.args.get('q', '').strip()
    normalized = normalize_search_query(raw_query)
    product_name = normalized['query']
    
    if not product_name:
        return jsonify({'error': 'Product name is required'}), 400
    
    if len(product_name) < 2:
        return jsonify({'error': 'Product name too short'}), 400
    
    # Record normalized search query for useful history and trends.
    search_record = SearchHistory(search_query=product_name, results_count=0)
    
    try:
        # Check if product already exists
        product = Product.query.filter_by(name=product_name).first()
        
        if not product:
            product = Product(name=product_name)
            db.session.add(product)
            db.session.flush()  # Get the product ID
        
        # Perform scraping in background or directly
        results = perform_scraping(
            product,
            product_name,
            source_site=normalized['source_site'],
            source_url=normalized['source_url']
        )

        source_site = normalized['source_site']
        source_result = results.get(source_site) if source_site else None
        if source_result and source_result.get('name'):
            product.name = source_result['name']
        
        search_record.results_count = sum(1 for r in results.values() if r.get('price'))
        db.session.add(search_record)
        db.session.commit()
        
        return jsonify({
            'product': product.to_dict(),
            'results': results
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def perform_scraping(product, product_name, source_site=None, source_url=None):
    """
    Perform actual scraping from multiple sites
    """
    results = {}
    
    # Initialize scrapers
    scrapers = {
        'amazon': AmazonScraper(),
        'flipkart': FlipkartScraper(),
        'meesho': MeeshoScraper()
    }
    
    # Scrape each site
    for site_key, scraper in scrapers.items():
        if site_key == source_site and source_url and hasattr(scraper, 'execute_product_url'):
            result = scraper.execute_product_url(source_url)
            if result.get('price') is None:
                result = scraper.execute_search(product_name)
        else:
            result = scraper.execute_search(product_name)

        # If query came from a direct product URL, preserve it for that source site.
        if site_key == source_site and source_url and not result.get('url'):
            result['url'] = source_url

        results[site_key] = result

        storage_key = 'ebay' if site_key == 'meesho' else site_key
        
        # Update product record
        if result.get('url'):
            setattr(product, f'{storage_key}_url', result['url'])

        if result.get('price') is not None:
            setattr(product, f'{storage_key}_price', result['price'])
            
            # Also save to price records for history
            price_record = PriceRecord(
                product_id=product.id,
                site=site_key,
                price=result['price'],
                url=result['url']
            )
            db.session.add(price_record)
    
    return results

@search_bp.route('/results/<int:product_id>', methods=['GET'])
def get_product_results(product_id):
    """Get detailed results for a product"""
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200
