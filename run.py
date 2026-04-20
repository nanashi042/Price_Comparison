import os
from app import create_app, db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get config from environment or default to development
config_name = os.getenv('FLASK_ENV', 'development')

# Create app
app = create_app(config_name)

if __name__ == '__main__':
    with app.app_context():
        # Create database tables
        db.create_all()
        print("Database tables created successfully!")
    
    # Run the Flask application
    debug = config_name == 'development'
    app.run(debug=debug, host='0.0.0.0', port=5000)
