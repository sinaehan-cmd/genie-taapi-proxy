# ======================================================
# 🌐 view_routes.py – Genie Render Server (Full Stream Edition)
# ======================================================
from flask import Blueprint, jsonify, Response, stream_with_context
from urllib.parse import unquote
from utils.google_sheets import get_sheets_service
from config import SHEET_ID
from datetime import datetime
from itertools import zip_longest
import json

bp = Blueprint("view_routes", __name__)

# ------------------------------------------------------
# 📘 HTML 보기용 (기본 뷰)
# ------------------------------------------------------
@bp.route("/view-html/<path:sheet_name>")
def view_html(sheet_name):
    try:
        decoded = unquote(sheet_name)
        service = get_sheets_service()
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=decoded
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
        </style></head><body>
        <h2>📘 {decoded}</h2>
        {table_html}
        </body></html>"""

        response = Response(html, mimetype="text/html")
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        return f"<h3>오류 발생: {e}</h3>", 500


# ------------------------------------------------------
# 🪄 GPT 접근용 HTML+JSON (미리보기 버전)
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
            return "<h3>No data found</h3>"

        headers = values[0]
        rows = [dict(zip(headers, row)) for row in values[1:]]
        payload = {
            "sheet": decoded,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "count": len(rows),
            "data": rows
        }
        json_str = json.dumps(payload, ensure_ascii=False, indent=2)

        html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'>
        <title>{decoded} JSON View</title>
        <style>
            body {{ font-family: monospace; background: #111; color: #0f0; padding: 20px; }}
            pre {{ white-space: pre-wrap; word-wrap: break-word; }}
        </style></head><body>
        <h2>🧩 JSON Data – {decoded}</h2>
        <pre>{json_str}</pre>
        </body></html>"""

        response = Response(html, mimetype="text/html")
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Cache-Control"] = "no-store"
        return response

    except Exception as e:
        error_html = f"<h3>오류 발생: {e}</h3>"
        return Response(error_html, mimetype="text/html", status=500)


# ------------------------------------------------------
# 🧩 완전 무제한 JSON 스트리밍 (GPT, API 전용)
# ------------------------------------------------------
@bp.route("/view-json/<path:sheet_name>")
def view_json(sheet_name):
    try:
        decoded = unquote(sheet_name)
        service = get_sheets_service()
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=decoded
        ).execute()
        values = result.get("values", [])
        if not values:
            return Response(json.dumps({"error": "No data found"}), mimetype="application/json", status=404)

        headers = values[0]
        rows = [dict(zip_longest(headers, row, fillvalue="")) for row in values[1:]]
        total_count = len(rows)

        # ✅ 스트리밍 제너레이터 함수
        def generate():
            yield '{'
            yield f'"sheet":"{decoded}",'
            yield f'"timestamp":"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}",'
            yield f'"count":{total_count},'
            yield '"data":['
            for i, row in enumerate(rows):
                safe_row = {k: (v if isinstance(v, str) else str(v)) for k, v in row.items()}
                if i > 0:
                    yield ","
                yield json.dumps(safe_row, ensure_ascii=False)
            yield "]}"
            print(f"[DEBUG] streamed rows={total_count}", flush=True)

        # ✅ 무제한 스트리밍 응답
        return Response(
            stream_with_context(generate()),
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "no-store",
                "Connection": "close"
            }
        )

    except Exception as e:
        return Response(json.dumps({"error": str(e)}), mimetype="application/json", status=500)
