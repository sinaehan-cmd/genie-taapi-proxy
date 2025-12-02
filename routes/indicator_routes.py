# routes/indicator_routes.py
from flask import Blueprint, request, jsonify
from services.taapi_service import fetch_indicator

bp = Blueprint("indicator_routes", __name__)

@bp.route("/indicator")
def get_indicator():
    indicator = request.args.get("indicator")
    symbol = request.args.get("symbol")
    interval = request.args.get("interval")
    period = request.args.get("period")  # EMA 사용 가능

    if not indicator or not symbol or not interval:
        return jsonify({"error": "missing params"}), 400

    data = fetch_indicator(indicator, symbol, interval, period)
    return jsonify(data)
