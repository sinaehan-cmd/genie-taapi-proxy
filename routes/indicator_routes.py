from flask import Blueprint, request, jsonify
from services.taapi_service import fetch_indicator

bp = Blueprint("indicator", __name__, url_prefix="/indicator")

@bp.route("", methods=["GET"])
def get_indicator():
    try:
        indicator = request.args.get("indicator")
        symbol = request.args.get("symbol", "BTC/USDT")
        interval = request.args.get("interval", "1h")

        if not indicator:
            return jsonify({"error": "indicator is required"}), 400

        # period 제거!
        data = fetch_indicator(indicator, symbol, interval)

        print("🔥 DEBUG /indicator result:", data)

        return jsonify(data)

    except Exception as e:
        print("❌ ERROR inside /indicator:", str(e))
        return jsonify({"error": str(e)}), 500
