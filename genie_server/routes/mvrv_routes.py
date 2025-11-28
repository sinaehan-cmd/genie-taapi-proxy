from flask import Blueprint, jsonify
from genie_server.utils.mvrv_fetcher import get_mvrv_data

bp = Blueprint("mvrv_routes", __name__)

@bp.route("/mvrv", methods=["GET", "POST"])
def mvrv():
    """
    Return MVRV_Z + market_cap + realized_cap + raw values
    """
    try:
        data = get_mvrv_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
