from flask import Flask

def create_app():
    app = Flask(__name__)
    
    from src.app.routes import api
    app.register_blueprint(api)
    
    return app

