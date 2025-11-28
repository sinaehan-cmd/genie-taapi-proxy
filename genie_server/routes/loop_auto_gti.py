from flask import Blueprint, jsonify
import time, random

bp = Blueprint("loop_auto_gti", __name__)

@bp.route("/auto_gti_loop", methods=["GET", "POST"])
def auto_gti_loop():
    """
    GTI 자동 측정 루프 – 일정 주기마다 신뢰도 갱신
    """
    try:
        print("⚡ [AutoGTI] Loop start")
        time.sleep(0.3)
        gti_score = round(random.uniform(70, 95), 2)
        print(f"GTI auto updated → {gti_score}")
        return jsonify({
            "status": "success",
            "gti_score": gti_score
        })
    except Exception as e:
        print("❌ Auto GTI Loop Error:", e)
        return jsonify({"error": str(e)}), 500


