from flask import Blueprint, request, jsonify

# 기존 TAAPI 서비스
from services.taapi_service import (
    taapi_rsi,
    taapi_ema,
    taapi_macd
)

# 새로 추가되는 내부 계산 서비스
from services.dominance_service import (
    calc_dominance_4h,
    calc_dominance_1d
)
from services.mvrv_service import calc_mvrv_z


bp = Blueprint("indicator", __name__)


# --------------------------------------------------------
# 🔷 기존: RSI / EMA / MACD (절대 수정 X)
# --------------------------------------------------------
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
        # MACD
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



# --------------------------------------------------------
# 🔶 새로 추가되는 계산 기반 지표 라우트
# --------------------------------------------------------

@bp.route("/dominance/4h", methods=["GET"])
def dominance_4h():
    """최근 dominance(1h) 4개 평균"""
    try:
        value = calc_dominance_4h()
        return jsonify({"indicator": "dominance_4h", "value": value})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/dominance/1d", methods=["GET"])
def dominance_1d():
    """최근 dominance(1h) 24개 평균"""
    try:
        value = calc_dominance_1d()
        return jsonify({"indicator": "dominance_1d", "value": value})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/mvrv_z", methods=["GET"])
def mvrv_z():
    """Genie 근사식 MVRV Z-Score"""
    try:
        value = calc_mvrv_z()
        return jsonify({"indicator": "mvrv_z", "value": value})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
