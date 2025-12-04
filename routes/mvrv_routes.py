# routes/mvrv_routes.py

from flask import Blueprint, jsonify
from services.mvrv_service import calc_mvrv_z
import requests

bp = Blueprint("mvrv", __name__)

def get_btc_price():
    """Coingecko → Binance 순으로 가격 조회"""
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
            timeout=5
        ).json()
        return float(r["bitcoin"]["usd"])
    except:
        try:
            r = requests.get(
                "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT",
                timeout=5
            ).json()
            return float(r["price"])
        except:
            return None


@bp.route("/mvrv", methods=["GET"])
def mvrv_calc():
    price = get_btc_price()
    if price is None:
        return jsonify({"error": "price fetch failed"}), 500

    z = calc_mvrv_z(price)

    return jsonify({
        "BTC_Price": price,
        "MVRV_Z": z
    })
