from flask import Blueprint

search_bp = Blueprint('search', __name__, url_prefix='/api/search')
history_bp = Blueprint('history', __name__, url_prefix='/api/history')

from app.routes import search_routes, history_routes
