from flask import Blueprint, request, jsonify
from services.sheet_service import append_row
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
    # 1) (구버전) record_values 제거됨
    #     - genie_indicator_calc.py는 현재 시스템에서 사용 안 함
    #     - dominance/btc_price는 market_service에서 수집됨
    # -----------------------------------------

    # -----------------------------------------
    # 2) Google Sheet에 행 추가
    # -----------------------------------------
    try:
        append_row(sheet, values)
    except Exception as e:
        return jsonify({"error": f"append_row 실패: {e}"}), 500

    return jsonify({"status": "ok"})
