from flask import Blueprint, jsonify
import datetime

bp = Blueprint("loop_learning", __name__)

@bp.route("/learning_loop")
def learning_loop():
    """
    지니 자기학습 루프 – GTI 결과 기반 보정
    """
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("🧠 [LearningLoop] 시작:", now)

        # 간단한 시뮬레이션: 최근 GTI 변동 패턴에 따른 보정률 계산
        correction = round((datetime.datetime.now().second % 10) * 0.1, 2)
        print("보정률:", correction)

        return jsonify({
            "timestamp": now,
            "learning_rate": correction,
            "result": "Success"
        })
    except Exception as e:
        print("❌ Learning Loop Error:", e)
        return jsonify({"error": str(e)}), 500
