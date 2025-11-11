from flask import Flask
from flask_cors import CORS
from routes import register_routes
from config import log_env_info

def create_app():
    app = Flask(__name__)
    CORS(app)
    log_env_info()
    register_routes(app)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8080)
