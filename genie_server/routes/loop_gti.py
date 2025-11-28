from flask import Blueprint, jsonify
import datetime, random
from genie_server.utils.writer_helper import send_to_sheet

bp = Blueprint("loop_gti", __name__)

@bp.route("/gti_loop", methods=["GET", "POST"])
def gti_loop():
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        score = round(random.uniform(60, 95), 2)

        # 🔥 기록 추가
        send_to_sheet("genie_gti_log", [now, score])

        return jsonify({"timestamp": now, "gti_score": score})

    except Exception as e:
        print("❌ gti_loop Error:", e)
        return jsonify({"error": str(e)}), 500
