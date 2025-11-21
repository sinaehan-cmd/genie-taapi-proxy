# genie_server/routes/indicator_routes.py
from flask import Blueprint, request, jsonify
from genie_server.utils.taapi_client import fetch_indicator

bp_indicator = Blueprint("indicator", __name__)

@bp_indicator.route("/indicator")
def indicator():
    """Return TAAPI indicator value as JSON (for Google Sheets)."""
    try:
        indicator = request.args.get("indicator", "rsi")
        symbol = request.args.get("symbol", "BTC/USDT")
        interval = request.args.get("interval", "1h")
        period = request.args.get("period")

        value = fetch_indicator(indicator, symbol, interval, period)

        if value is None:
            return jsonify({"error": "value_not_found"}), 200

        return jsonify({
            "indicator": indicator,
            "symbol": symbol,
            "interval": interval,
            "value": value
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
