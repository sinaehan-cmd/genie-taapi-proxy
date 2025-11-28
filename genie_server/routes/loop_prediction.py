# -*- coding: utf-8 -*-
# ======================================================
# 🔮 Genie Prediction Loop (Ultra Stable v3.0)
# — 절대 죽지 않는 가격 예측 루프
# ======================================================

from flask import Blueprint, jsonify
import requests, datetime

bp = Blueprint("prediction_loop", __name__)

# ------------------------------------------------------
# 안전한 fetch
# ------------------------------------------------------
def safe_get(url):
    try:
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None


@bp.route("/prediction_loop", methods=["GET", "POST"])
def prediction_loop():
    """
    🔮 가격 기반 예측 — 구조 변경/timeout 시 절대 죽지 않는 버전
    """
    try:
        now = datetime.datetime.now()
        print(f"🔮 [PredictionLoop] 시작: {now}")

        price = None

        # ======================================================
        # 1) Coindesk v1 (가장 안정적)
        # ======================================================
        cd = safe_get("https://api.coindesk.com/v1/bpi/currentprice.json")
        if cd and "bpi" in cd:
            try:
                price = float(cd["bpi"]["USD"]["rate_float"])
            except:
                pass

        # ======================================================
        # 2) Coinbase fallback
        # ======================================================
        if price is None:
            cb = safe_get("https://api.coinbase.com/v2/prices/BTC-USD/spot")
            try:
                if cb and "data" in cb and "amount" in cb["data"]:
                    price = float(cb["data"]["amount"])
            except:
                pass

        # ======================================================
        # 3) Paprika fallback (구조 변경 대비)
        # ======================================================
        if price is None:
            pk = safe_get("https://api.coinpaprika.com/v1/tickers/btc-bitcoin")
            try:
                if pk and "quotes" in pk and "USD" in pk["quotes"]:
                    price = float(pk["quotes"]["USD"]["price"])
            except:
                pass

        # ======================================================
        # 4) CoinGecko simple price (최후의 안전장치)
        # ======================================================
        if price is None:
            cg = safe_get(
                "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
            )
            try:
                price = float(cg["bitcoin"]["usd"])
            except:
                pass

        # ======================================================
        # 5) 모든 API 실패 → price가 None이면 1 넣기 (auto_loop 보호)
        # ======================================================
        if price is None:
            print("⚠️ BTC 가격 fetch 실패 → 예측 가격을 1로 설정하여 루프 보호")
            price = 1

        # ------------------------------------------------------
        # 예측 로직 (임시)
        # ------------------------------------------------------
        prediction = "상승" if price > 50000 else "관망"

        return jsonify({
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "BTC": price,
            "prediction": prediction
        })

    except Exception as e:
        print("❌ Prediction Loop Error:", e)

        # 절대 500으로 죽지 않도록 fallback 응답
        return jsonify({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "BTC": 1,
            "prediction": "관망",
            "error": str(e)
        }), 200
