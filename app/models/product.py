from app import db
from datetime import datetime

class Product(db.Model):
    """Product model to store product data"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    amazon_url = db.Column(db.String(500))
    amazon_price = db.Column(db.Float)
    flipkart_url = db.Column(db.String(500))
    flipkart_price = db.Column(db.Float)
    ebay_url = db.Column(db.String(500))
    ebay_price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    price_records = db.relationship('PriceRecord', backref='product', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def to_dict(self):
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'amazon': {
                'price': self.amazon_price,
                'url': self.amazon_url
            },
            'flipkart': {
                'price': self.flipkart_price,
                'url': self.flipkart_url
            },
            'ebay': {
                'price': self.ebay_price,
                'url': self.ebay_url
            },
            'cheapest': self._get_cheapest(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def _get_cheapest(self):
        """Get the cheapest option"""
        prices = {
            'amazon': self.amazon_price,
            'flipkart': self.flipkart_price,
            'ebay': self.ebay_price
        }
        prices = {k: v for k, v in prices.items() if v is not None}
        
        if not prices:
            return None
        
        cheapest_site = min(prices, key=lambda site: prices[site])
        return {
            'site': cheapest_site,
            'price': prices[cheapest_site]
        }
