from flask import Blueprint, jsonify
import requests, datetime

bp = Blueprint("prediction_loop", __name__)

# 가격 가져오기 — 응답 구조 변화 대비 다중 fallback
def get_price_safe(data, *keys):
    for k in keys:
        if k in data:
            return float(data[k])
    return None

@bp.route("/prediction_loop", methods=["GET", "POST"])
def prediction_loop():
    """
    가격 기반 간단 예측 루프 — 구조 변경에도 절대 죽지 않는 버전
    """
    try:
        print(f"🔮 [PredictionLoop] 시작: {datetime.datetime.now()}")

        # 가격 데이터 가져오기 (여러 출처 fallback)
        sources = [
            "https://api.coindesk.com/v1/bpi/currentprice.json",
            "https://api.coinbase.com/v2/prices/BTC-USD/spot",
            "https://api.coinpaprika.com/v1/tickers/btc-bitcoin"
        ]

        price = None
        for url in sources:
            try:
                r = requests.get(url, timeout=6).json()

                # Coindesk 구조
                if "bpi" in r:
                    price = float(r["bpi"]["USD"]["rate_float"])
                    break

                # Coinbase 구조
                if "data" in r and "amount" in r["data"]:
                    price = float(r["data"]["amount"])
                    break

                # Paprika 구조
                if "quotes" in r and "USD" in r["quotes"]:
                    price = float(r["quotes"]["USD"]["price"])
                    break

            except Exception:
                pass

        if price is None:
            # 안전장치
            price = 0

        # 간단한 예측 로직
        prediction = "상승" if price > 50000 else "관망"

        return jsonify({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "BTC": price,
            "prediction": prediction
        })

    except Exception as e:
        print("❌ Prediction Loop Error:", e)
        return jsonify({"error": str(e)}), 500
