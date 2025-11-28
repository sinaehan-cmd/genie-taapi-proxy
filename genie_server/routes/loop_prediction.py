# prediction_loop.py
from flask import Blueprint, jsonify
import requests, datetime
from genie_server.utils.writer_helper import send_to_sheet

bp = Blueprint("prediction_loop", __name__)

@bp.route("/prediction_loop", methods=["POST","GET"])
def prediction_loop():
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 가격 가져오기 (fallback)
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        price = requests.get(url, timeout=5).json().get("price")
        price = float(price) if price else 0

        pred = "상승" if price > 50000 else "관망"

        # 시트 기록
        row = [now, price, pred]
        send_to_sheet("genie_predictions", row)

        return jsonify({
            "timestamp": now, 
            "BTC": price, 
            "prediction": pred
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
