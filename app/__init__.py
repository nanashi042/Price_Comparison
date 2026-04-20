from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app(config_name='development'):
    """Application factory"""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app = Flask(
        __name__,
        template_folder=os.path.join(project_root, 'templates'),
        static_folder=os.path.join(project_root, 'static')
    )
    
    # Load configuration
    from config.config import config
    app.config.from_object(config[config_name])
    
    # Initialize database
    db.init_app(app)

    # Import models before create_all so SQLAlchemy registers all tables.
    from app import models  # noqa: F401
    
    # Create instance folder if it doesn't exist
    try:
        os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'instance'), exist_ok=True)
    except OSError:
        pass
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from app.routes import search_bp, history_bp
    app.register_blueprint(search_bp)
    app.register_blueprint(history_bp)
    
    # Register main routes
    from app.routes.main_routes import register_main_routes
    register_main_routes(app)
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def server_error(error):
        return {'error': 'Server error'}, 500
    
    return app
