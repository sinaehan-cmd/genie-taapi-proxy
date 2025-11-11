from flask import Blueprint, jsonify
import requests, datetime, json
from utils.helpers import safe_float
from config import SHEET_ID

bp = Blueprint("loop_prediction", __name__)

@bp.route("/prediction_loop")
def prediction_loop():
    """
    BTC/ETH 가격 및 RSI 기반 예측 루프
    """
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("🔮 [PredictionLoop] 시작:", now)

        btc_data = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd").json()
        btc = safe_float(btc_data["bitcoin"]["usd"])
        eth = safe_float(btc_data["ethereum"]["usd"])

        # 단순 예시 예측식 (지니 예측루프 내부에서 실제 계산 가능)
        prediction = {
            "timestamp": now,
            "BTC": btc,
            "ETH": eth,
            "prediction": "상승" if btc > 100000 else "관망"
        }

        print("📈 예측결과:", prediction)
        return jsonify(prediction)
    except Exception as e:
        print("❌ Prediction Loop Error:", e)
        return jsonify({"error": str(e)}), 500
