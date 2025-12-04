# main.py — Genie Server v2025.12
# Flask + 내부 라우트 + 자동 루프 스케줄러 통합본

from flask import Flask
import threading

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

    @app.route("/")
    def home():
        return "Genie Server v2025.12 — OK"

    # 디버그 라우트 추가
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
# 자동 루프 스레드 안전하게 실행
# (Gunicorn worker 중복 실행 방지)
# ────────────────────────────────
def start_background_loop():
    print("🚀 Genie Master Loop 시작 (thread)")
    start_master_loop()


# Gunicorn 환경에서는 __name__ == "__main__" 가 실행되지 않으므로
# worker 부팅 시 스레드를 1번만 생성
threading.Thread(target=start_background_loop, daemon=True).start()


# ────────────────────────────────
# 개발용 Standalone 실행
# ────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
