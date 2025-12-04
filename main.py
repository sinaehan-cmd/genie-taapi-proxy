# main.py — Genie Server v2025.12
# Flask + 내부 라우트 + 자동 루프 스케줄러 통합본

from flask import Flask

# ────────────────────────────────
# Blueprint Imports (라우트)
# ────────────────────────────────
from routes.view_routes import view_bp
from routes.write_routes import write_bp
from routes.loop_routes import loop_bp
from routes.dominance_routes import bp as dominance_bp
from routes.mvrv_routes import bp as mvrv_bp
from routes.indicator_routes import bp as indicator_bp

# ★ 핵심: 자동 루프 스케줄러
from app_feedback_v1_1 import start_master_loop


# ────────────────────────────────
# Flask Application Factory
# ────────────────────────────────
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


# ────────────────────────────────
# Gunicorn / Render에서 사용할 Flask app
# ────────────────────────────────
app = create_app()


# ────────────────────────────────
# ★ 자동 루프 시작 (진짜 핵심)
# ────────────────────────────────
# Render / Gunicorn에서도 thread 정상 동작함
start_master_loop()


# ────────────────────────────────
# 개발용 Standalone 실행
# ────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
