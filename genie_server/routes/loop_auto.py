from flask import Blueprint, jsonify
import requests, time
from utils.helpers import generate_briefing_id
from genie_server.config import SHEET_ID, GENIE_ACCESS_KEY

bp = Blueprint("loop_auto", __name__)

@bp.route("/auto_loop")
def auto_loop():
    """
    지니 자동 브리핑 루프 (8시간마다 작동하는 브리핑 생성)
    """
    try:
        start = time.time()
        print("🌀 [AutoLoop] 실행 시작")

        # (예시) 내부 루프 실행 순서
        for endpoint in [
            "/prediction_loop",
            "/gti_loop",
            "/learning_loop",
            "/system_log",

            # ⭐ 여기 추가: MVRV_Z 자동 수집 루프
            "/mvrv_loop",
        ]:
            print(f"📡 호출: {endpoint}")
            r = requests.get(f"http://localhost:8080{endpoint}")
            print(f"↳ 응답: {r.status_code}")

        duration = round(time.time() - start, 2)
        return jsonify({
            "status": "✅ Auto Loop completed",
            "duration_sec": duration,
            "briefing_id": generate_briefing_id()
        })
    except Exception as e:
        print("❌ AutoLoop Error:", e)
        return jsonify({"error": str(e)}), 500

