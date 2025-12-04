# main.py — Genie Server v2025.12
# Flask + 내부 라우트 + 자동 루프 스케줄러 통합본

from flask import Flask
import os

# ────────────────────────────────
# Blueprint Imports (라우트)
# ────────────────────────────────
from routes.view_routes import view_bp
from routes.write_routes import write_bp
from routes.loop_routes import loop_bp
from routes.dominance_routes import bp as dominance_bp
from routes.mvrv_routes import bp as mvrv_bp
from routes.indicator_routes import bp as indicator_bp

# 자동 루프 모듈
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

    # 홈 라우트
    @app.route("/")
    def home():
        return "Genie Server v2025.12 — OK"

    # 디버그 라우트
    @app.route("/debug/routes")
    def debug_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(str(rule))
        return "<br>".join(routes)

    return app


# ────────────────────────────────
# Gunicorn / Render에서 사용할 Flask app
# ────────────────────────────────
app = create_app()


# ────────────────────────────────
# ★ WORKER 프로세스에서만 루프 시작
# ────────────────────────────────
# Render worker command에 반드시 추가:
#   env WORKER=true python3 -m gunicorn main:app
# Web service에는 WORKER 환경변수 없이 실행
# ────────────────────────────────

if os.getenv("WORKER", "false").lower() == "true":
    print("🚀 WORKER detected — Starting Master Loop")
    start_master_loop()
else:
    print("⚠️ Not a worker process — Loop disabled")


# ────────────────────────────────
# 개발용 Standalone 실행
# ────────────────────────────────
if __name__ == "__main__":
    # 개발환경에서는 loop도 같이 실행하도록 설정
    start_master_loop()
    app.run(host="0.0.0.0", port=5000)
