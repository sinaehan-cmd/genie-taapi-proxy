from flask import Blueprint, request, jsonify
from services.sheet_service import append_row
from services.genie_indicator_calc import record_values   # ★ 지니 계산 모듈
import datetime

write_bp = Blueprint("write_routes", __name__)


@write_bp.route("/write", methods=["POST"])
def write():
    body = request.json
    sheet = body.get("sheet")
    values = body.get("values")

    if not sheet or not values:
        return jsonify({"error": "sheet 또는 values 누락"}), 400

    # -----------------------------------------
    # 🔥 1) values 배열에서 dominance / btc_price 꺼내기
    # -----------------------------------------
    try:
        # 인덱스는 네 실제 시트 구조에 따라 다름
        # 내가 자동 감지형으로 짜줄게
        dominance_value = None
        btc_price = None

        # BTC/USD 값 찾기
        for v in values:
            if isinstance(v, (int, float)) and btc_price is None:
                btc_price = v  # 첫 번째 숫자를 BTC로 간주 (안전 fallback)
                break

        # Dominance 값 찾기
        for v in values:
            if isinstance(v, (int, float)) and 0 < v < 100:
                dominance_value = v
                # 0~100% 사이 값이면 dominance 가능성 높음
                break

        # -----------------------------------------
        # 🔥 2) 지니 계산용 값 기록 (중요!)
        # -----------------------------------------
        record_values(
            dominance=dominance_value,
            btc_price=btc_price
        )

    except Exception as e:
        print(f"⚠️ record_values 에러 발생: {e}")

    # -----------------------------------------
    # 🔥 3) 기존처럼 Google Sheet에 row 추가
    # -----------------------------------------
    try:
        append_row(sheet, values)
    except Exception as e:
        return jsonify({"error": f"append_row 실패: {e}"}), 500

    return jsonify({"status": "ok"})
