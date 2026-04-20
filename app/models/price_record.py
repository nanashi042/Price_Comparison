from app import db
from datetime import datetime

class PriceRecord(db.Model):
    """Price history record model"""
    __tablename__ = 'price_records'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    site = db.Column(db.String(50), nullable=False)  # amazon, flipkart, ebay
    price = db.Column(db.Float, nullable=False)
    url = db.Column(db.String(500))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<PriceRecord {self.site} - {self.price}>'
    
    def to_dict(self):
        """Convert record to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'site': self.site,
            'price': self.price,
            'url': self.url,
            'recorded_at': self.recorded_at.isoformat()
        }
