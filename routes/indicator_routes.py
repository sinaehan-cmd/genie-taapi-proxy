from flask import Blueprint, request, jsonify
from services.taapi_service import taapi_rsi, taapi_ema, taapi_macd
from services.genie_indicator_calc import (
    record_values,
    get_dominance_4h,
    get_dominance_1d,
    calc_mvrv_z
)

bp = Blueprint("indicator", __name__)


@bp.route("/indicator_extra", methods=["GET"])
def get_indicator_extra():
    """
    지니 계산 지표:
    - dominance_4h
    - dominance_1d
    - mvrv_z
    """
    t = request.args.get("type")

    if t == "dominance_4h":
        v = get_dominance_4h()
        return jsonify({"indicator": "dominance_4h", "value": v})

    if t == "dominance_1d":
        v = get_dominance_1d()
        return jsonify({"indicator": "dominance_1d", "value": v})

    if t == "mvrv_z":
        v = calc_mvrv_z()
        return jsonify({"indicator": "mvrv_z", "value": v})

    return jsonify({"error": "unknown type"}), 400
