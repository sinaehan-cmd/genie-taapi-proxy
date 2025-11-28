from flask import Blueprint, jsonify
import datetime
from genie_server.utils.writer_helper import send_to_sheet

bp = Blueprint("loop_learning", __name__)

@bp.route("/learning_loop", methods=["GET", "POST"])
def learning_loop():
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        send_to_sheet("genie_briefing_log", [now, "learning_ok"])

        return jsonify({"timestamp": now, "status": "learning_ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
