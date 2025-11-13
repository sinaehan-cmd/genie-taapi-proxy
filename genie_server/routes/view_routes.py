# ======================================================
# 🌐 view_routes.py – Genie Render Server HTML + JSON (v2025.11.13-Final)
# ======================================================
from flask import Blueprint, Response
from urllib.parse import unquote
from utils.google_sheets import get_sheets_service
from config import SHEET_ID
from datetime import datetime
from itertools import zip_longest
import json

bp = Blueprint("view_routes", __name__)

# ------------------------------------------------------
# 📘 HTML 보기용
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

        resp = Response(html, mimetype="text/html")
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp

    except Exception as e:
        return f"<h3>오류 발생: {e}</h3>", 500


# ------------------------------------------------------
# 🧩 HTML에 JSON 포장 (GPT 접근용)
# ------------------------------------------------------
@bp.route("/view-html-json/<path:sheet_name>")
def view_html_json(sheet_name):
    try:
        decoded = unquote(sheet_name)
        service = get_sheets_service()
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range=decoded
        ).execute()
        values = result.get("values", [])

        if not values:
            html = "<h3>No data found</h3>"
        else:
            headers = values[0]
            rows = [dict(zip_longest(headers, row, fillvalue="")) for row in values[1:]]
            payload = {
                "sheet": decoded,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "count": len(rows),
                "data": rows,
            }
            json_str = json.dumps(payload, ensure_ascii=False, indent=2)
            html = f"""
            <!DOCTYPE html><html><head><meta charset='utf-8'>
            <title>{decoded} JSON View</title>
            <style>
                body {{ font-family: monospace; background: #111; color: #0f0; padding: 20px; }}
                pre {{ white-space: pre-wrap; word-wrap: break-word; }}
            </style></head><body>
            <h2>🧩 JSON Data – {decoded}</h2>
            <pre>{json_str}</pre>
            </body></html>
            """

        resp = Response(html, mimetype="text/html")
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Cache-Control"] = "no-store"
        return resp

    except Exception as e:
        err_html = f"<h3>오류 발생: {e}</h3>"
        return Response(err_html, mimetype="text/html", status=500)


# ------------------------------------------------------
# 🧩 JSON API (대용량 대응, 잘림 방지)
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
            return Response(json.dumps({"error": "No data found"}), mimetype="application/json")

        headers = values[0]
        rows = [dict(zip_longest(headers, row, fillvalue="")) for row in values[1:]]
        payload = {
            "sheet": decoded,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "count": len(rows),
            "data": rows,
        }

        json_str = json.dumps(payload, ensure_ascii=False)
        resp = Response(json_str, mimetype="application/json")
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Cache-Control"] = "no-store"
        return resp

    except Exception as e:
        err = {"error": str(e)}
        return Response(json.dumps(err, ensure_ascii=False), mimetype="application/json", status=500)
