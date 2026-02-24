from flask import Flask
from src.utils.logger import get_logger
logger = get_logger("src.app.__init__")

def create_app():
    app = Flask(__name__)
    
    from src.app.routes import api
    app.register_bluelogger.info(api)
    
    return app

