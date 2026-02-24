from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

VISUALIZATION_DIR = os.path.join(os.path.dirname(__file__), 'src', 'visualization')
TEMPLATE_DIR = os.path.join(VISUALIZATION_DIR, 'templates')
STATIC_DIR = os.path.join(VISUALIZATION_DIR, 'static')


def create_app():
    app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["60/minute"],
        storage_uri="memory://",
    )

    allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
    if allowed_origins_env:
        allowed_origins_list = [origin.strip() for origin in allowed_origins_env.split(",")]
    else:
        allowed_origins_list = ["http://localhost:5173", "http://127.0.0.1:5173"]

    CORS(app, origins=allowed_origins_list)

    from src.visualization.web.controllers import main
    app.register_blueprint(main)

    from src.app.routes import api
    app.register_blueprint(api)

    limiter.limit("10/minute")(app.view_functions.get("api.run_scheduler", lambda: None))

    from src.app.database import init_db
    init_db()

    return app


app = create_app()

if __name__ == '__main__':
    DATA_DIR = os.path.join(os.getcwd(), 'data', 'output')
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    app.run(debug=True, host='0.0.0.0', port=8001)
