# main.py — Genie Server v2025.12
# Flask + 내부 라우트 + 자동 루프 스케줄러 분리 안정판

import os
import threading
from flask import Flask

# ────────────────────────────────────────────
# Blueprint Routes
# ────────────────────────────────────────────
from routes.view_routes import view_bp
from routes.write_routes import write_bp
from routes.loop_routes import loop_bp
from routes.dominance_routes import bp as dominance_bp
from routes.mvrv_routes import bp as mvrv_bp
from routes.indicator_routes import bp as indicator_bp
from routes.loop_fix_routes import loop_fix_bp

# 자동 루프 모듈 (Worker에서만 실행됨)
from app_feedback_v1_1 import start_master_loop


# =====================================================================
# 🚀 Worker Mode Detection
#
# WORKER=true → 루프 자동 실행
# WORKER=false → 일반 Web 컨테이너 (루프 실행 금지)
# =====================================================================
IS_WORKER = os.getenv("WORKER", "false").lower() == "true"

print(f"🔧 Genie Server Booting... WORKER Mode = {IS_WORKER}")


# =====================================================================
# Flask Application Factory
# =====================================================================
def create_app():
    app = Flask(__name__)

    # 라우트 등록
    app.register_blueprint(view_bp)
    app.register_blueprint(write_bp)
    app.register_blueprint(loop_bp)
    app.register_blueprint(dominance_bp)
    app.register_blueprint(mvrv_bp)
    app.register_blueprint(indicator_bp)

    @app.route("/")
    def home():
        mode = "WORKER" if IS_WORKER else "WEB"
        return f"Genie Server v2025.12 — OK ({mode})"

    # 디버그용: 현재 등록된 라우트 확인
    @app.route("/debug/routes")
    def debug_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(str(rule))
        return "<br>".join(routes)

    return app


# =====================================================================
# Gunicorn이 불러갈 실제 app
# =====================================================================
app = create_app()


# =====================================================================
# 🔁 Worker 모드에서만 자동루프 실행 (절대 Web에서 실행 안 됨)
# =====================================================================
def start_background_loop():
    print("🚀 Worker Thread: Genie Master Loop 시작")
    start_master_loop()


if IS_WORKER:
    # Worker에서만 스레드로 루프 실행
    threading.Thread(target=start_background_loop, daemon=True).start()
    print("🟢 Worker: Master Loop Activated")
else:
    print("🔵 Web: Loop Disabled (API 전용)")


# =====================================================================
# Standalone 실행 (LOCAL 개발할 때만)
# =====================================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
