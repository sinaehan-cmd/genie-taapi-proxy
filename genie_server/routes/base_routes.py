from flask import Blueprint, jsonify
from datetime import datetime
from genie_server.config import SHEET_ID

bp = Blueprint("base", __name__)

@bp.route("/random.txt")
def random_txt():
    return (
        "Genie_Access_OK\nThis file exists to mark this domain as static-content safe.\nUpdated: 2025-11-05",
        200,
        {"Content-Type": "text/plain"},
    )

@bp.route("/test")
def test():
    return jsonify({
        "status": "✅ Running (Stable v3.0)",
        "sheet_id": SHEET_ID,
        "uptime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@bp.route("/")
def home():
    return jsonify({
        "status": "Genie Render Server ✅ (v3.0)",
        "routes": {
            "view": "/view-html/<sheet_name>",
            "write": "/write",
            "auto_loop": "/auto_loop",
            "prediction_loop": "/prediction_loop",
            "gti_loop": "/gti_loop",
            "learning_loop": "/learning_loop",
            "system_log": "/system_log",
        },
    })

