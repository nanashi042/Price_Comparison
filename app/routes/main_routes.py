from flask import render_template

# Register main routes with the app
def register_main_routes(app):
    @app.route('/')
    def index():
        """Serve the main page"""
        return render_template('index.html')
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return {'status': 'healthy'}, 200
