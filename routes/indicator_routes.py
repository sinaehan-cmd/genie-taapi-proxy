from flask import Blueprint, request, jsonify
from services.taapi_service import fetch_indicator

bp = Blueprint("indicator", __name__)


@bp.route("/indicator", methods=["GET"])
def get_indicator():
    """
    모든 지표 호출 통합 엔드포인트
    예시:
    /indicator?indicator=rsi&symbol=BTC/USDT&interval=1h&period=14
    """
    try:
        indicator = request.args.get("indicator")
        symbol = request.args.get("symbol", "BTC/USDT")
        interval = request.args.get("interval", "1h")
        period = request.args.get("period", None)

        value = fetch_indicator(indicator, symbol, interval, period)

        return jsonify({
            "indicator": indicator,
            "symbol": symbol,
            "interval": interval,
            "period": period,
            "value": value
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
