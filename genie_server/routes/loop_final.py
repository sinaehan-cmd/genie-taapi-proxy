from flask import Blueprint, jsonify
import requests, datetime

bp = Blueprint("loop_final", __name__)

@bp.route("/final_briefing" methods=["GET", "POST"])
def final_briefing():
    """
    모든 루프 결과를 모아서 최종 브리핑 생성
    """
    try:
        print("📊 [FinalBriefing] 수집 시작")
        endpoints = ["prediction_loop", "gti_loop", "learning_loop", "system_log"]
        results = {}
        for ep in endpoints:
            try:
                r = requests.get(f"http://localhost:8080/{ep}")
                results[ep] = r.json()
            except Exception as inner_e:
                results[ep] = {"error": str(inner_e)}

        summary = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": "최종 브리핑 데이터 수집 완료",
            "modules": results
        }
        print("✅ Final briefing complete.")
        return jsonify(summary)
    except Exception as e:
        print("❌ FinalBriefing Error:", e)
        return jsonify({"error": str(e)}), 500

