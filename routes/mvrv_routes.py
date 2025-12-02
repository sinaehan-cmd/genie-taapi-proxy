from flask import Blueprint, jsonify, request
from services.mvrv_service import calc_mvrv_z, update_price_buffer

bp = Blueprint("mvrv", __name__)

@bp.route("/mvrv", methods=["POST", "GET"])
def mvrv_get():
    """
    GET → Apps Script용 MVRV-Z 반환
    POST → Collector에서 가격 업데이트
    """

    if request.method == "POST":
        data = request.json
        update_price_buffer(data.get("price"))
        return jsonify({"status": "updated"})

    return jsonify({"MVRV_Z": calc_mvrv_z()})
