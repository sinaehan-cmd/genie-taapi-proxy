from flask import Blueprint, jsonify, render_template
from services.sheet_service import read_sheet

view_bp = Blueprint("view_routes", __name__)


@view_bp.route("/view-json/<sheet>")
def view_json(sheet):
    data = read_sheet(sheet)

    if not data or len(data) < 2:
        return jsonify({"error": "no data"}), 404

    # 첫 줄 = 헤더(변하지 않음)
    header = data[0]

    # 최근 239줄 (헤더 제외)
    rows = data[-239:]

    dict_rows = []
    for row in rows:
        row_obj = {}
        for i, col_name in enumerate(header):
            row_obj[col_name] = row[i] if i < len(row) else None
        dict_rows.append(row_obj)

    return jsonify(dict_rows)


@view_bp.route("/view-html/<sheet>")
def view_html(sheet):
    data = read_sheet(sheet)
    return render_template("table_view.html", rows=data[-240:])
