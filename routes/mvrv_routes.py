from flask import Blueprint, jsonify
from services.mvrv_service import get_mvrv_data

bp = Blueprint("mvrv", __name__)

@bp.route("/mvrv", methods=["GET"])
def mvrv_endpoint():
    """
    MVRV_Z 계산 API
    """
    data = get_mvrv_data()
    return jsonify(data)
