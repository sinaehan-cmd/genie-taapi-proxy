from flask import Blueprint, jsonify
from services.market_service import mvrv_run   # ★ 반드시 여기로!

bp = Blueprint("mvrv", __name__, url_prefix="/mvrv")

@bp.route("/run", methods=["GET"])
def run_mvrv():
    """
    단순 MVRV 값 반환
    """
    result = mvrv_run()
    return jsonify(result)
