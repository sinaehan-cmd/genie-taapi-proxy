from flask import Blueprint, jsonify
import requests, datetime
from genie_server.utils.writer_helper import send_to_sheet

bp = Blueprint("mvrv_routes", __name__)

@bp.route("/mvrv", methods=["GET", "POST"])
def mvrv_route():
    try:
        r = requests.get("https://api.coinpaprika.com/v1/tickers/btc-bitcoin", timeout=6)
        mvrv = r.json()["quotes"]["USD"]["percent_from_price_ath"]
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        send_to_sheet("genie_data_v5", [now, "MVRV_Z", mvrv])

        return jsonify({"timestamp": now, "MVRV_Z": mvrv})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
