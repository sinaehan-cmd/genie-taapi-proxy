from flask import Blueprint, jsonify, render_template
from services.sheet_service import read_sheet

view_bp = Blueprint("view_routes", __name__)

@view_bp.route("/view-json/<sheet>")
def view_json(sheet):
    data = read_sheet(sheet)

    # 데이터 없으면 에러 반환
    if not data or len(data) < 2:
        return jsonify({"error": "no data"}), 404

    # 최근 240줄만 사용
    sliced = data[-240:]

    # 첫 줄 = 헤더
    header = sliced[0]
    rows = sliced[1:]

    # 헤더와 매핑해서 JSON object 리스트로 변환
    dict_rows = []
    for row in rows:
        row_obj = {}
        for i, col_name in enumerate(header):
            if i < len(row):
                row_obj[col_name] = row[i]
            else:
                row_obj[col_name] = None
        dict_rows.append(row_obj)

    return jsonify(dict_rows)


@view_bp.route("/view-html/<sheet>")
def view_html(sheet):
    data = read_sheet(sheet)

    # HTML 출력은 기존처럼 값 그대로
    return render_template("table_view.html", rows=data[-240:])
