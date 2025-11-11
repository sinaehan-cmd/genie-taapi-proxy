from flask import Blueprint, request, jsonify, Response
from urllib.parse import unquote
from utils.google_sheets import get_sheets_service
from config import SHEET_ID
from flask_cors import CORS
import json
from datetime import datetime

bp = Blueprint("view_routes", __name__)

@bp.route("/view-html/<path:sheet_name>")
def view_html(sheet_name):
    try:
        decoded = unquote(sheet_name)
        service = get_sheets_service()
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range=decoded).execute()
        values = result.get("values", [])
        if not values:
            return "<h3>No data found</h3>"
        table_html = "<table border='1' cellspacing='0' cellpadding='4'>" + "".join(
            "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in values
        ) + "</table>"
        html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'>
        <title>{decoded}</title><style>body{{font-family:sans-serif}}</style></head>
        <body><h2>📘 {decoded}</h2>{table_html}</body></html>"""
        response = Response(html, mimetype="text/html")
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        return f"<h3>오류: {e}</h3>", 500

@bp.route("/view-json/<path:sheet_name>")
def view_json(sheet_name):
    decoded = unquote(sheet_name)
    service = get_sheets_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range=decoded).execute()
    values = result.get("values", [])
    if not values: return "<h3>No data</h3>"
    headers = values[0]
    rows = [dict(zip(headers, row)) for row in values[1:]]
    response = {
        "sheet": decoded,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(rows),
        "data": rows[-5:],
    }
    html = f"<pre>{json.dumps(response, ensure_ascii=False, indent=2)}</pre>"
    return html

