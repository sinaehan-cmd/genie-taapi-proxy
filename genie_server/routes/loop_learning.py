# learning_loop.py
from flask import Blueprint, jsonify
import datetime
from genie_server.utils.writer_helper import send_to_sheet

bp = Blueprint("learning_loop", __name__)

@bp.route("/learning_loop", methods=["POST","GET"])
def learning_loop():
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        send_to_sheet("genie_briefing_log",
                      [now, "learning_ok"])

        return jsonify({"timestamp": now, "learning": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
