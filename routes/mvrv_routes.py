# routes/mvrv_routes.py

from flask import Blueprint, jsonify
from services.mvrv_service import calc_mvrv_z, update_price_buffer
import requests

bp = Blueprint("mvrv", __name__)

def fetch_btc_price():
    """Binance 가격을 직접 가져와 서버에서 계산"""
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5).json()
        return float(r["price"])
    except:
        return None


@bp.route("/mvrv", methods=["GET"])
def get_mvrv():
    # 1) BTC 가격 직접 가져오기
    price = fetch_btc_price()

    if price is None:
        return jsonify({"MVRV_Z": None, "error": "price_fetch_failed"})

    # 2) 버퍼 업데이트
    update_price_buffer(price)

    # 3) 계산 수행
    z = calc_mvrv_z()

    return jsonify({
        "BTC_Price": price,
        "MVRV_Z": z
    })
