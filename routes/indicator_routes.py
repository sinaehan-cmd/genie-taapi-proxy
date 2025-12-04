# routes/indicator_routes.py
from flask import Blueprint, request, jsonify
from services.taapi_service import taapi_rsi, taapi_ema, taapi_macd

bp = Blueprint("indicator_routes", __name__)

@bp.route("/indicator", methods=["GET"])
def get_indicator():
    """
    /indicator?indicator=rsi&symbol=BTC/USDT&interval=1h
    /indicator?indicator=ema&symbol=BTC/USDT&interval=1h&period=20
    /indicator?indicator=macd&symbol=BTC/USDT&interval=1h

    Apps Script는 아래 형식의 "단일 값 또는 숫자 필드"를 기대한다:

    { "value": 47.22 }
    { "value": 93000.22 }
    { "macd": 200, "signal": 180, "hist": -20 }
    """

    ind = request.args.get("indicator")
    symbol = request.args.get("symbol", "BTC/USDT")
    interval = request.args.get("interval", "1h")

    # --------------------------------------------------------
    # RSI
    # --------------------------------------------------------
    if ind == "rsi":
        raw = taapi_rsi(symbol=symbol, interval=interval)
        # raw → {"value": 47.22}
        return jsonify({
            "indicator": "rsi",
            "value": raw.get("value")
        })

    # --------------------------------------------------------
    # EMA
    # --------------------------------------------------------
    if ind == "ema":
        period = request.args.get("period", 20)
        raw = taapi_ema(symbol=symbol, interval=interval, period=period)
        # raw → {"value": 93000.12}
        return jsonify({
            "indicator": "ema",
            "value": raw.get("value")
        })

    # --------------------------------------------------------
    # MACD
    # --------------------------------------------------------
    if ind == "macd":
        raw = taapi_macd(symbol=symbol, interval=interval)
        # raw → {"macd": ..., "signal": ..., "hist": ...}
        return jsonify({
            "indicator": "macd",
            "macd": raw.get("macd"),
            "signal": raw.get("signal"),
            "hist": raw.get("hist")
        })

    return jsonify({"error": "unknown indicator"}), 400
