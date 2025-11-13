# ======================================================
# 🌐 view_routes.py – Genie Render Server JSON+HTML Viewer (v2025.11.13-p10-ziplongest)
# ======================================================
from flask import Blueprint, jsonify, Response
from urllib.parse import unquote
from utils.google_sheets import get_sheets_service
from config import SHEET_ID
from datetime import datetime
from itertools import zip_longest  # ✅ 추가

bp = Blueprint("view_routes", __name__)

# ------------------------------------------------------
# 📘 HTML 보기용 (그대로 유지)
# ------------------------------------------------------
@bp.route("/view-html/<path:sheet_name>")
def view_html(sheet_name):
    try:
        decoded = unquote(sheet_name)
        service = get_sheets_service()
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range=decoded
        ).execute()
        values = result.get("values", [])
        if not values:
            return "<h3>No data found</h3>"

        table_html = "<table border='1' cellspacing='0' cellpadding='4'>" + "".join(
            "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in values
        ) + "</table>"

        html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'>
        <title>{decoded}</title>
        <style>
            body {{ font-family: sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ padding: 6px 10px; border: 1px solid #ccc; }}
            tr:nth-child(even) {{ background: #f9f9f9; }}
        </style>
        </head><body>
        <h2>📘 {decoded}</h2>
        {table_html}
        </body></html>"""

        response = Response(html, mimetype="text/html")
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        return f"<h3>오류 발생: {e}</h3>", 500


# ------------------------------------------------------
# 🧩 JSON API (열 개수 불일치 완전 보정 + 최근 168행)
# ------------------------------------------------------
@bp.route("/view-json/<path:sheet_name>")
def view_json(sheet_name):
    try:
        decoded = unquote(sheet_name)
        service = get_sheets_service()
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range=decoded
        ).execute()
        values = result.get("values", [])
        if not values:
            return jsonify({"error": "No data found"}), 404

        headers = values[0]

        # ✅ zip_longest로 열 개수 자동 맞추기
        rows = [dict(zip_longest(headers, row, fillvalue="")) for row in values[1:]]

        # ✅ 최근 168행만 반환
        filtered_rows = rows[-168:]

        response = {
            "sheet": decoded,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "count": len(filtered_rows),
            "data": filtered_rows,
        }

        resp = jsonify(response)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Cache-Control"] = "no-store"
        return resp

    except Exception as e:
        return jsonify({"error": str(e)}), 500
