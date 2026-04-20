from app import db
from datetime import datetime

class SearchHistory(db.Model):
    """Search history model"""
    __tablename__ = 'search_history'
    
    id = db.Column(db.Integer, primary_key=True)
    search_query = db.Column(db.String(255), nullable=False)
    results_count = db.Column(db.Integer)
    searched_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<SearchHistory {self.search_query}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'search_query': self.search_query,
            'results_count': self.results_count,
            'searched_at': self.searched_at.isoformat()
        }
