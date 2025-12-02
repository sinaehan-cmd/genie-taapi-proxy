from flask import Blueprint, request, jsonify
from services.taapi_service import (
    taapi_rsi,
    taapi_ema,
    taapi_macd
)

bp = Blueprint("indicator", __name__)


@bp.route("/indicator", methods=["GET"])
def get_indicator():
    """
    모든 지표 호출 – Render는 절대 자기 자신을 다시 부르지 않는다.
    RSI / EMA / MACD를 TAAPI 원본에서 가져와 응답.
    """

    try:
        indicator = request.args.get("indicator")
        symbol = request.args.get("symbol", "BTC/USDT")
        interval = request.args.get("interval", "1h")
        period = request.args.get("period", None)

        # ------------------------------
        # RSI
        # ------------------------------
        if indicator == "rsi":
            r = taapi_rsi(symbol, interval, period)
            return jsonify({
                "indicator": "rsi",
                "value": r.get("value", "값없음")
            })

        # ------------------------------
        # EMA
        # ------------------------------
        if indicator == "ema":
            e = taapi_ema(symbol, interval, period)
            return jsonify({
                "indicator": "ema",
                "value": e.get("value", "값없음")
            })

        # ------------------------------
        # MACD (전용 구조)
        # ------------------------------
        if indicator == "macd":
            m = taapi_macd(symbol, interval)
            return jsonify({
                "indicator": "macd",
                "valueMACD": m["macd"],
                "valueMACDSignal": m["signal"],
                "valueMACDHist": m["hist"]
            })

        # ------------------------------
        # 잘못된 경우
        # ------------------------------
        return jsonify({"error": "unknown indicator"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
