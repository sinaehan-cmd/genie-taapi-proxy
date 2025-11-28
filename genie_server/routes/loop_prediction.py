from flask import Blueprint, jsonify
import requests, datetime
from genie_server.utils.writer_helper import send_to_sheet

bp = Blueprint("prediction_loop", __name__)

@bp.route("/prediction_loop", methods=["GET", "POST"])
def prediction_loop():
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=6)
        price = float(r.json().get("price", 0))

        pred = "상승" if price > 50000 else "관망"

        # 🔥 시트 기록 추가
        send_to_sheet("genie_predictions", [now, price, pred])

        return jsonify({
            "timestamp": now,
            "BTC": price,
            "prediction": pred
        })

    except Exception as e:
        print("❌ PredictionLoop Error:", e)
        return jsonify({"error": str(e)}), 500
