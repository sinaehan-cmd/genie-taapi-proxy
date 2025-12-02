# routes/mvrv_routes.py
from flask import Blueprint, jsonify
from services.mvrv_service import calculate_mvrv_z

bp = Blueprint("mvrv", __name__)

@bp.route("/mvrv_z", methods=["GET"])
def get_mvrv_z():
    """
    Genie 내부 가격 데이터(genie_data_v5)를 기반으로
    MVRV Z-Score를 계산해 반환하는 API.
    """
    try:
        value, info = calculate_mvrv_z()

        return jsonify({
            "mvrv_z": value,
            "source": info,
            "status": "ok"
        })

    except Exception as e:
        return jsonify({
            "mvrv_z": None,
            "error": str(e),
            "status": "error"
        }), 500
