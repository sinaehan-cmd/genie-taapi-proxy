from flask import Flask
from routes.view_routes import view_bp
from routes.write_routes import write_bp
from routes.loop_routes import loop_bp

app = Flask(__name__)

# Blueprint 등록
app.register_blueprint(view_bp)
app.register_blueprint(write_bp)
app.register_blueprint(loop_bp)

@app.route("/")
def home():
    return "Genie Server v2025.12 — OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

