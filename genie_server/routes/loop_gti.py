from flask import Blueprint, jsonify
import datetime, random

bp = Blueprint("loop_gti", __name__)

@bp.route("/gti_loop")
def gti_loop():
    """
    GTI 계산 루프 – Genie Trust Index 산출
    """
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        score = round(random.uniform(75, 95), 2)
        print(f"🔵 [GTI Loop] {now} → GTI Score = {score}")

        result = {
            "timestamp": now,
            "GTI_Score": score,
            "trend": "상승신뢰" if score > 85 else "보통신뢰"
        }
        return jsonify(result)
    except Exception as e:
        print("❌ GTI Loop Error:", e)
        return jsonify({"error": str(e)}), 500
