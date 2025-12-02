# routes/indicator_routes.py
from flask import Blueprint, request, jsonify
from services.taapi_service import get_taapi_indicator   # 🔥 fetch_indicator 대신 이걸 사용
from utils.response import success, error

bp = Blueprint("indicator", __name__, url_prefix="/indicator")

@bp.route("", methods=["GET"])
def indicator_handler():
    """
    안전 패치 버전:
    - 절대 /indicator 내부에서 다시 /indicator 호출하지 않음
    - 모든 TAAPI 호출은 services/taapi_service.py의 get_taapi_indicator() 단일 경로로만 실행
    - timeout 발생 시 바로 '값없음' 반환 → 무한 재시도 방지
    """

    indicator = request.args.get("indicator")
    symbol = request.args.get("symbol", "BTC/USDT")
    interval = request.args.get("interval", "1h")
    period = request.args.get("period")

    if not indicator:
        return error("indicator parameter is required", 400)

    # 🔥 핵심: 절대 이 라우트 내부에서 자기 자신(/indicator)을 다시 호출하지 않음
    result = get_taapi_indicator(
        indicator=indicator,
        symbol=symbol,
        interval=interval,
        period=period
    )

    # 실패 처리
    if result is None or result == "값없음":
        return jsonify({"value": "값없음"}), 200

    # 정상
    return jsonify(result), 200
