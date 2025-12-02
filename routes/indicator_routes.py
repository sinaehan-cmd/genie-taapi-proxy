from flask import Blueprint, request, jsonify
from services.taapi_service import taapi_rsi, taapi_ema, taapi_macd

bp = Blueprint("indicator", __name__)

@bp.route("/indicator", methods=["GET"])
def get_indicator():
    indicator = request.args.get("indicator")
    symbol = request.args.get("symbol", "BTC/USDT")
    interval = request.args.get("interval", "1h")
    period = request.args.get("period")

    # ----- RSI -----
    if indicator == "rsi":
        r = taapi_rsi(symbol, interval, period)
        return jsonify({
            "value": r["value"] if r["value"] is not None else "값없음"
        })

    # ----- EMA -----
    if indicator == "ema":
        e = taapi_ema(symbol, interval, period)
        return jsonify({
            "value": e["value"] if e["value"] is not None else "값없음"
        })

    # ----- MACD -----
    if indicator == "macd":
        m = taapi_macd(symbol, interval)
        return jsonify({
            "valueMACD": m["macd"],
            "valueMACDSignal": m["signal"],
            "valueMACDHist": m["hist"]
        })

    return jsonify({"error": "unknown indicator"}), 400
