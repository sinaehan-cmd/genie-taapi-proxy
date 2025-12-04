# routes/indicator_routes.py
from flask import Blueprint, request, jsonify
from services.taapi_service import taapi_rsi, taapi_ema, taapi_macd

bp = Blueprint("indicator_routes", __name__)

@bp.route("/indicator", methods=["GET"])
def get_indicator():
    """
    Collector v9.2 는 이렇게 호출함:
      /indicator?indicator=rsi&symbol=BTC/USDT&interval=1h
      /indicator?indicator=ema&symbol=BTC/USDT&interval=1h&period=20
      /indicator?indicator=macd&symbol=BTC/USDT&interval=1h

    따라서 'indicator=' 파라미터를 기준으로 동작하도록 수정.
    """

    ind = request.args.get("indicator")   # <-- 핵심 변경
    symbol = request.args.get("symbol", "BTC/USDT")
    interval = request.args.get("interval", "1h")
    period = request.args.get("period", "20")  # EMA 용

    # -------------------------
    # RSI
    # -------------------------
    if ind == "rsi":
        v = taapi_rsi(symbol, interval)
        return jsonify({
            "indicator": "rsi",
            "value": v
        })

    # -------------------------
    # EMA
    # -------------------------
    if ind == "ema":
        v = taapi_ema(symbol, interval, period)
        return jsonify({
            "indicator": "ema",
            "value": v
        })

    # -------------------------
    # MACD
    # -------------------------
    if ind == "macd":
        v = taapi_macd(symbol, interval)
        return jsonify({
            "indicator": "macd",
            **v      # macd, signal, hist 포함
        })

    # -------------------------
    # unknown
    # -------------------------
    return jsonify({"error": "unknown indicator"}), 400
