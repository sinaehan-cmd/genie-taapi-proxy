# genie_server/routes/indicator_routes.py
from flask import Blueprint, request, jsonify
import requests
import os

bp = Blueprint("indicator", __name__)

TAAPI_KEY = os.getenv("TAAPI_KEY")
BASE_URL = "https://api.taapi.io"

@bp.route("/indicator")
def indicator():
    """Return TAAPI indicator value as JSON (Genie Sheets 호출용)."""
    try:
        indicator = request.args.get("indicator", "rsi")
        symbol = request.args.get("symbol", "BTC/USDT")
        interval = request.args.get("interval", "1h")
        period = request.args.get("period")

        params = {
            "secret": TAAPI_KEY,
            "exchange": "binance",
            "symbol": symbol,
            "interval": interval
        }
        if period:
            params["period"] = period

        url = f"{BASE_URL}/{indicator}"
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        # RSI
        if "value" in data:
            return jsonify({
                "indicator": indicator,
                "symbol": symbol,
                "interval": interval,
                "value": data["value"]
            })

        # MACD
        elif "valueMACD" in data:
            return jsonify({
                "indicator": indicator,
                "symbol": symbol,
                "interval": interval,
                "value": data["valueMACD"]
            })

        else:
            return jsonify({"error": "no_value", "raw": data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
