# routes/indicator_routes.py
from flask import Blueprint, request, jsonify
from services.taapi_service import taapi_rsi, taapi_ema, taapi_macd
from services.genie_indicator_calc import (
    get_dominance_4h,
    get_dominance_1d,
    calc_mvrv_z
)

bp = Blueprint("indicator_routes", __name__)


@bp.route("/indicator", methods=["GET"])
def get_indicator():
    """
    type 파라미터에 따라 해당 지표 반환
    예:
      /indicator?type=rsi&symbol=BTC&interval=1h
      /indicator?type=dominance_4h
      /indicator?type=mvrv
    """
    t = request.args.get("type")

    # -------------------------
    # TAAPI 지표들
    # -------------------------
    if t == "rsi":
        symbol = request.args.get("symbol", "BTC")
        interval = request.args.get("interval", "1h")
        return jsonify({
            "indicator": "rsi",
            "value": taapi_rsi(symbol, interval)
        })

    if t == "ema":
        symbol = request.args.get("symbol", "BTC")
        interval = request.args.get("interval", "1h")
        return jsonify({
            "indicator": "ema",
            "value": taapi_ema(symbol, interval)
        })

    if t == "macd":
        symbol = request.args.get("symbol", "BTC")
        interval = request.args.get("interval", "1h")
        return jsonify({
            "indicator": "macd",
            "value": taapi_macd(symbol, interval)
        })

    # -------------------------
    # 지니 계산 지표들
    # -------------------------
    if t == "dominance_4h":
        return jsonify({
            "indicator": "dominance_4h",
            "value": get_dominance_4h()
        })

    if t == "dominance_1d":
        return jsonify({
            "indicator": "dominance_1d",
            "value": get_dominance_1d()
        })

    if t == "mvrv":
        return jsonify({
            "indicator": "mvrv_z",
            "value": calc_mvrv_z()
        })

    return jsonify({"error": "unknown type"}), 400
