# routes/auto_loop_routes.py

from flask import Blueprint, jsonify
from loops.auto_loop import run_auto_loop

auto_loop_bp = Blueprint("auto_loop", __name__)

# GET 또는 POST 모두 지원할 수 있게 methods 옵션 추가
@auto_loop_bp.route("/loop/auto", methods=["GET", "POST"])
def auto_loop_run():
    """
    자동 루프 1회 실행 엔드포인트
    """
    try:
        result = run_auto_loop()
        return jsonify({
            "status": "success",
            "result": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
