# routes/indicator_routes.py
from flask import Blueprint, request, jsonify
from services.taapi_service import taapi_rsi, taapi_ema, taapi_macd
from services.genie_indicator_calc import (
    get_dominance_4h,
    get_dominance_1d,
)
from services.mvrv_service import calc_mvrv_z

bp = Blueprint("indicator_routes", __name__)


@bp.route("/indicator", methods=["GET"])
def get_indicator():
    """
    Collector 호출 형식과 100% 호환되도록 정리된 버전

    예:
      /indicator?indicator=rsi&symbol=BTC/USDT&interval=1h
      /indicator?indicator=ema&symbol=BTC/USDT&interval=1h&period=20
      /indicator?indicator=macd&symbol=BTC/USDT&interval=1h
    """

    ind = request.args.get("indicator")

    # ---------- RSI ----------
    if ind == "rsi":
        symbol = request.args.get("symbol", "BTC/USDT")
        interval = request.args.get("interval", "1h")
        return jsonify({
            "indicator": "rsi",
            "value": taapi_rsi(symbol, interval)
        })

    # ---------- EMA ----------
    if ind == "ema":
        symbol = request.args.get("symbol", "BTC/USDT")
        interval = request.args.get("interval", "1h")
        period = request.args.get("period", "20")
        return jsonify({
            "indicator": "ema",
            "value": taapi_ema(symbol, interval, period)
        })

    # ---------- MACD ----------
    if ind == "macd":
        symbol = request.args.get("symbol", "BTC/USDT")
        interval = request.args.get("interval", "1h")
        return jsonify({
            "indicator": "macd",
            "value": taapi_macd(symbol, interval)
        })

    # ---------- Dominance 4h ----------
    if ind == "dominance_4h":
        return jsonify({
            "indicator": "dominance_4h",
            "value": get_dominance_4h()
        })

    # ---------- Dominance 1d ----------
    if ind == "dominance_1d":
        return jsonify({
            "indicator": "dominance_1d",
            "value": get_dominance_1d()
        })

    # ---------- MVRV ----------
    if ind == "mvrv":
        return jsonify({
            "indicator": "mvrv",
            "value": calc_mvrv_z()
        })

    return jsonify({"error": "unknown indicator"}), 400
