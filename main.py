from flask import Flask

from routes.view_routes import view_bp
from routes.write_routes import write_bp
from routes.loop_routes import loop_bp
from routes.dominance_routes import bp as dominance_bp
from routes.mvrv_routes import bp as mvrv_bp
from routes.indicator_routes import bp as indicator_bp

# ★ 자동 루프 추가
from app_feedback_v1_1 import start_master_loop


def create_app():
    app = Flask(__name__)

    # Blueprint 등록
    app.register_blueprint(view_bp)
    app.register_blueprint(write_bp)
    app.register_blueprint(loop_bp)
    app.register_blueprint(dominance_bp)
    app.register_blueprint(mvrv_bp)
    app.register_blueprint(indicator_bp)

    @app.route("/")
    def home():
        return "Genie Server v2025.12 — OK"

    return app


# Flask app 생성
app = create_app()

# 🔥🔥🔥 여기에 자동 루프 꼭 붙여야 한다! (지금 너에게 없는 부분)
start_master_loop()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
