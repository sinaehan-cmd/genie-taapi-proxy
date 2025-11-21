from flask import Flask
from flask_cors import CORS
from genie_server.routes import register_routes
from genie_server.config import log_env_info

def create_app():
    app = Flask(__name__)
    CORS(app)
    log_env_info()
    register_routes(app)
    return app

# 🔥 gunicorn이 찾는 app 객체는 여기 있어야 함!!
app = create_app()

if __name__ == "__main__":
    # 로컬 실행할 때만 이 블록 실행됨
    app.run(host="0.0.0.0", port=8080)
