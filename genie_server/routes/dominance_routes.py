from flask import Blueprint, jsonify
import requests, datetime
from genie_server.utils.writer_helper import send_to_sheet

bp = Blueprint("dominance_routes", __name__)

@bp.route("/dominance/snapshot", methods=["GET", "POST"])
def dom_snapshot():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/global", timeout=5)
        dom = r.json()["data"]["market_cap_percentage"]["btc"]
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        send_to_sheet("genie_alert_log", [now, "DominanceSnapshot", dom])

        return jsonify({"timestamp": now, "dominance": dom})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
