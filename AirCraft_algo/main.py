from flask import Flask
from flask_cors import CORS
import os

# Template and static folders for visualization
VISUALIZATION_DIR = os.path.join(os.path.dirname(__file__), 'src', 'visualization')
TEMPLATE_DIR = os.path.join(VISUALIZATION_DIR, 'templates')
STATIC_DIR = os.path.join(VISUALIZATION_DIR, 'static')

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
    
    # Enable CORS for all routes
    CORS(app)
    
    # Register visualization blueprint
    from src.visualization.web.controllers import main
    app.register_blueprint(main)
    
    # Register API blueprint
    from src.app.routes import api
    app.register_blueprint(api)
    
    return app

app = create_app()

if __name__ == '__main__':
    # Ensure data directory exists
    DATA_DIR = os.path.join(os.getcwd(), 'data', 'output')
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    app.run(debug=True, host='0.0.0.0', port=8001)



