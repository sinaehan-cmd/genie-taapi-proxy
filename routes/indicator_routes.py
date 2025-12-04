# routes/indicator_routes.py

from flask import Blueprint, request, jsonify
from services.taapi_service import taapi_rsi, taapi_ema, taapi_macd
from services.genie_indicator_calc import (
    get_dominance_4h,
    get_dominance_1d,
    calc_mvrv_z
)

bp = Blueprint("indicator_routes", __name__)


@bp.route("/indicator", methods=["GET"])
def get_indicator():
    """
    Collector v9.2 완전 호환 버전
    -----------------------------------
    지원되는 요청 형태 (둘 다 허용):

      /indicator?indicator=rsi&symbol=BTC&interval=1h
      /indicator?type=rsi&symbol=BTC&interval=1h

    Collector는 indicator= 을 보내므로
    indicator → type 자동 매핑 필요.
    """

    # indicator 또는 type 받기 (둘 중 하나)
    t = request.args.get("indicator") or request.args.get("type")

    # =============================
    # 🔹 TAAPI RSI
    # =============================
    if t == "rsi":
        symbol = request.args.get("symbol", "BTC")
        interval = request.args.get("interval", "1h")
        value = taapi_rsi(symbol, interval)
        return jsonify({
            "indicator": "rsi",
            "value": value
        })

    # =============================
    # 🔹 TAAPI EMA
    # =============================
    if t == "ema":
        symbol = request.args.get("symbol", "BTC")
        interval = request.args.get("interval", "1h")
        period = request.args.get("period", 20)
        value = taapi_ema(symbol, interval, period)
        return jsonify({
            "indicator": "ema",
            "value": value
        })

    # =============================
    # 🔹 TAAPI MACD
    # =============================
    if t == "macd":
        symbol = request.args.get("symbol", "BTC")
        interval = request.args.get("interval", "1h")
        macd_val = taapi_macd(symbol, interval)

        # Collector는 valueMACD 필드 읽음
        return jsonify({
            "indicator": "macd",
            "valueMACD": macd_val
        })

    # =============================
    # 🔹 Genie 계산형 Indicator
    # =============================
    if t == "dominance_4h":
        return jsonify({
            "indicator": "dominance_4h",
            "value": get_dominance_4h()
        })

    if t == "dominance_1d":
        return jsonify({
            "indicator": "dominance_1d",
            "value": get_dominance_1d()
        })

    if t == "mvrv":
        return jsonify({
            "indicator": "mvrv_z",
            "value": calc_mvrv_z()
        })

    # =============================
    # 🔹 Unknown
    # =============================
    return jsonify({"error": "unknown indicator type"}), 400
