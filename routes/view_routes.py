from flask import Blueprint, jsonify, render_template
from services.google_sheets import read_sheet

view_bp = Blueprint("view_routes", __name__)

@view_bp.route("/view-json/<sheet>")
def view_json(sheet):
    data = read_sheet(sheet)
    return jsonify(data[-240:])   # 최근 10일 (1시간 간격 기준)

@view_bp.route("/view-html/<sheet>")
def view_html(sheet):
    data = read_sheet(sheet)
    return render_template("table_view.html", rows=data[-240:])

