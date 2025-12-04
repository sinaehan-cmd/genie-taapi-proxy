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
    Collector 호환:
      /indicator?indicator=rsi&symbol=BTC/USDT&interval=1h
      /indicator?indicator=ema&symbol=BTC/USDT&interval=1h&period=20
      /indicator?indicator=macd&symbol=BTC/USDT&interval=1h

    지니 계산:
      /indicator?indicator=dominance_4h
      /indicator?indicator=dominance_1d
      /indicator?indicator=mvrv
    """

    # Collector가 주는 파라미터 이름 = indicator
    t = request.args.get("indicator")

    # -------------------------
    # TAAPI 지표들
    # -------------------------
    if t == "rsi":
        symbol = request.args.get("symbol", "BTC/USDT")
        interval = request.args.get("interval", "1h")
        v = taapi_rsi(symbol, interval)
        return jsonify({"value": v})

    if t == "ema":
        symbol = request.args.get("symbol", "BTC/USDT")
        interval = request.args.get("interval", "1h")
        period = request.args.get("period", 20)
        v = taapi_ema(symbol, interval)
        return jsonify({"value": v})

    if t == "macd":
        symbol = request.args.get("symbol", "BTC/USDT")
        interval = request.args.get("interval", "1h")
        v = taapi_macd(symbol, interval)
        return jsonify(v)

    # -------------------------
    # 지니 계산 지표들
    # -------------------------
    if t == "dominance_4h":
        return jsonify({"value": get_dominance_4h()})

    if t == "dominance_1d":
        return jsonify({"value": get_dominance_1d()})

    if t == "mvrv":
        return jsonify({"value": calc_mvrv_z()})

    return jsonify({"error": "unknown indicator"}), 400
