from flask import Blueprint, jsonify
import requests

bp = Blueprint("dominance", __name__)

@bp.route("/dominance", methods=["GET"])
def get_dominance():
    try:
        url = "https://api.coingecko.com/api/v3/global"
        r = requests.get(url, timeout=8).json()

        data = r.get("data", {})
        dominance = data.get("market_cap_percentage", {}).get("btc")
        dominance_eth = data.get("market_cap_percentage", {}).get("eth")
        total_mc = data.get("total_market_cap", {}).get("usd")

        return jsonify({
            "btc_dominance": dominance,
            "eth_dominance": dominance_eth,
            "total_market_cap_usd": total_mc
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
