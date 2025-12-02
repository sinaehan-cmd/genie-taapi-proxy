from flask import Flask
from routes.view_routes import bp as view_bp
from routes.write_routes import bp as write_bp
from routes.loop_routes import bp as loop_bp
from routes.dominance_routes import bp as dominance_bp
from routes.mvrv_routes import bp as mvrv_bp

# ─────────────────────────────────────────────
# Flask Application Factory
# ─────────────────────────────────────────────
def create_app():
    app = Flask(__name__)

    # Blueprint 등록
    app.register_blueprint(view_bp)
    app.register_blueprint(write_bp)
    app.register_blueprint(loop_bp)
    app.register_blueprint(dominance_bp)
    app.register_blueprint(mvrv_bp)

    @app.route("/")
    def home():
        return "Genie Server v2025.12 — OK"

    return app


# ─────────────────────────────────────────────
# Standalone 실행 (개발용)
# Render / Gunicorn 환경에서는 create_app()만 호출됨
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
