# ======================================================
# 🌐 view_routes.py – Genie Render Server HTML + JSON (v2025.11.28-Fixed)
# ======================================================
from flask import Blueprint, Response, request, redirect
from urllib.parse import unquote
from genie_server.utils.google_sheets import get_sheets_service
from genie_server.config import SHEET_ID
from datetime import datetime
from itertools import zip_longest
import json, time

bp = Blueprint("view_routes", __name__)

# ------------------------------------------------------
# 🚫 캐시 방지용 nocache 파라미터 자동 추가 (GET 전용)
# ------------------------------------------------------
@bp.before_app_request
def append_nocache_param():
    """
    ❗ GET 요청만 nocache를 추가한다.
    ❗ POST/PUT/PATCH/DELETE 같은 write 요청은 절대 리다이렉트하지 않는다.
    """
    if request.method != "GET":
        return None

    # 정적 파일, favicon 등 제외
    if request.path.startswith("/static") or "favicon" in request.path:
        return None

    # 이미 nocache가 포함되어 있으면 그대로 사용
    if "nocache" in request.args:
        return None

    # nocache 파라미터 새로 붙여서 GET 전용 리다이렉트
    timestamp = int(time.time())
    new_url = f"{request.path}?nocache={timestamp}"

    if request.query_string:
        qs = request.query_string.decode()
        new_url = f"{request.path}?{qs}&nocache={timestamp}"

    return redirect(new_url)


# ------------------------------------------------------
# 📘 HTML 보기
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
# 🧩 HTML에 JSON 데이터 표시 (GPT-friendly)
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
        return Response(f"<h3>오류 발생: {e}</h3>", mimetype="text/html", status=500)


# ------------------------------------------------------
# 🧩 순수 JSON API (가장 안전)
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

        LIMIT = 168
        if len(rows) > LIMIT:
            rows = rows[-LIMIT:]

        payload = {
            "sheet": decoded,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "count": len(rows),
            "limit": LIMIT,
            "data": rows,
        }

        return Response(json.dumps(payload, ensure_ascii=False), mimetype="application/json")

    except Exception as e:
        err = {"error": str(e)}
        return Response(json.dumps(err, ensure_ascii=False), mimetype="application/json", status=500)


# ------------------------------------------------------
# 🔒 모든 응답 캐시 비활성화
# ------------------------------------------------------
@bp.after_app_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
