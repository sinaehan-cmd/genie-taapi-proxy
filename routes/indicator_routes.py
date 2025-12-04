from flask import Blueprint, request, jsonify
from services.taapi_service import taapi_rsi, taapi_ema, taapi_macd
from services.genie_indicator_calc import (
    record_values,
    get_dominance_4h,
    get_dominance_1d,
    calc_mvrv_z
)

bp = Blueprint("indicator", __name__)

# ---------------------------------------------------------
# 🔥 1) Apps Script / Genie Collector 기본 호출 라우트
#     (RSI · EMA · MACD → TAAPI 호출)
# ---------------------------------------------------------
@bp.route("/indicator", methods=["GET"])
def get_indicator():
    indicator = request.args.get("indicator")
    symbol = request.args.get("symbol", "BTC/USDT")
    interval = request.args.get("interval", "1h")
    period = request.args.get("period")

    # ------------------------------
    # RSI
    # ------------------------------
    if indicator == "rsi":
        return jsonify(taapi_rsi(symbol, interval, period))

    # ------------------------------
    # EMA
    # ------------------------------
    if indicator == "ema":
        return jsonify(taapi_ema(symbol, interval, period))

    # ------------------------------
    # MACD
    # ------------------------------
    if indicator == "macd":
        return jsonify(taapi_macd(symbol, interval))

    return jsonify({"error": "unknown indicator"}), 400


# ---------------------------------------------------------
# 🔥 2) 지니 내부 확장 계산 라우트
#     (dominance_4h · dominance_1d · mvrv_z)
# ---------------------------------------------------------
@bp.route("/indicator_extra", methods=["GET"])
def get_indicator_extra():
    """
    지니 자체 계산 지표:
    - dominance_4h
    - dominance_1d
    - mvrv_z
    """
    t = request.args.get("type")

    if t == "dominance_4h":
        v = get_dominance_4h()
        return jsonify({"indicator": "dominance_4h", "value": v})

    if t == "dominance_1d":
        v = get_dominance_1d()
        return jsonify({"indicator": "dominance_1d", "value": v})

    if t == "mvrv_z":
        v = calc_mvrv_z()
        return jsonify({"indicator": "mvrv_z", "value": v})

    return jsonify({"error": "unknown type"}), 400
