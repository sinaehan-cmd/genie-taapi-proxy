from flask import Blueprint, request, jsonify
from services.mvrv_service import calc_mvrv_z, update_price_buffer
from services.google_sheets import read_sheet_last_row

bp = Blueprint("mvrv_routes", __name__)

@bp.route("/mvrv/run", methods=["POST"])
def mvrv_run():
    # 1) 지니 데이터 시트에서 마지막 행 읽기
    row = read_sheet_last_row("genie_data_v5")

    if not row:
        return jsonify({"error": "no data"}), 500

    # 2) BTC 가격 열이 2번째 컬럼이라면 (인덱스 1)
    try:
        btc_price = float(row[1])
        update_price_buffer(btc_price)
    except:
        btc_price = None

    # 3) 계산
    z = calc_mvrv_z()

    return jsonify({
        "btc_price": btc_price,
        "mvrv_z": z
    })
