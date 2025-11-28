# gti_loop.py
from flask import Blueprint, jsonify
import random, datetime
from genie_server.utils.writer_helper import send_to_sheet

bp = Blueprint("gti_loop", __name__)

@bp.route("/gti_loop", methods=["POST","GET"])
def gti_loop():
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        score = round(random.uniform(60, 95), 2)

        send_to_sheet("genie_gti_log",
                      [now, score, "auto", "loop"])

        return jsonify({"timestamp": now, "gti_score": score})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
