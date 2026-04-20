from flask import request, jsonify
from app.routes import history_bp
from app.models import SearchHistory, PriceRecord, Product
from sqlalchemy import desc, func

@history_bp.route('/searches', methods=['GET'])
def get_search_history():
    """Get search history"""
    limit = request.args.get('limit', 50, type=int)
    
    searches = SearchHistory.query.order_by(desc(SearchHistory.searched_at)).limit(limit).all()
    
    return jsonify({
        'searches': [s.to_dict() for s in searches]
    }), 200

@history_bp.route('/prices/<int:product_id>', methods=['GET'])
def get_price_history(product_id):
    """Get price history for a product"""
    product = Product.query.get_or_404(product_id)
    limit = request.args.get('limit', 100, type=int)
    
    price_records = PriceRecord.query.filter_by(product_id=product_id).order_by(
        desc(PriceRecord.recorded_at)
    ).limit(limit).all()
    
    return jsonify({
        'product': product.to_dict(),
        'price_history': [p.to_dict() for p in price_records]
    }), 200

@history_bp.route('/trending', methods=['GET'])
def get_trending_searches():
    """Get trending searches"""
    limit = request.args.get('limit', 10, type=int)

    trending = (
        SearchHistory.query.with_entities(
            SearchHistory.search_query.label('search_query'),
            func.count(SearchHistory.id).label('search_count'),
            func.max(SearchHistory.searched_at).label('last_searched_at')
        )
        .group_by(SearchHistory.search_query)
        .order_by(desc('search_count'), desc('last_searched_at'))
        .limit(limit)
        .all()
    )

    return jsonify({
        'trending': [
            {
                'search_query': row.search_query,
                'search_count': row.search_count,
                'last_searched_at': row.last_searched_at.isoformat() if row.last_searched_at else None
            }
            for row in trending
        ]
    }), 200
