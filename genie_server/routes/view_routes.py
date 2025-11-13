# ======================================================
# 🌐 view_routes.py – Genie Render Server JSON+HTML Viewer (v2025.11.13-p2)
# ======================================================
from flask import Blueprint, request, jsonify, Response
from urllib.parse import unquote
from utils.google_sheets import get_sheets_service
from config import SHEET_ID
from flask_cors import CORS
import json
from datetime import datetime, timedelta

bp = Blueprint("view_routes", __name__)

# ------------------------------------------------------
# 📘 1️⃣ HTML 보기용 (기존 그대로 유지)
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
# 🧩 2️⃣ JSON API 보기용 (지니 자동 브리핑용)
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
        rows = [dict(zip(headers, row)) for row in values[1:]]

        # 🕒 최근 7일 데이터만 필터링 (지니 부하 방지)
        now = datetime.now()
        seven_days_ago = now - timedelta(days=7)
        filtered_rows = []

        for row in rows:
            ts_str = row.get("timestamp") or row.get("Timestamp") or row.get("시간") or row.get("기준시간")
            if not ts_str:
                continue
            ts = None
            # ✅ 여러 포맷 인식 (날짜 + 시간 대응)
            possible_formats = [
                "%Y-%m-%d %H:%M:%S",  # 2025-11-13 19:43:09
                "%Y-%m-%d",           # 2025-11-13
                "%Y/%m/%d %H:%M:%S",  # 2025/11/13 19:43:09
                "%Y/%m/%d",           # 2025/11/13
                "%Y.%m.%d %H:%M:%S",  # 2025.11.13 19:43:09
                "%Y.%m.%d"            # 2025.11.13
            ]
            for fmt in possible_formats:
                try:
                    ts = datetime.strptime(ts_str.strip(), fmt)
                    break
                except Exception:
                    continue
            if ts and ts >= seven_days_ago:
                filtered_rows.append(row)

        # 만약 타임스탬프 컬럼이 없거나 필터링 결과가 비면 최근 5행 표시
        if not filtered_rows:
            filtered_rows = rows[-5:]

        response = {
            "sheet": decoded,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "count": len(filtered_rows),
            "data": filtered_rows,
        }

        resp = jsonify(response)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Cache-Control"] = "no-store"
        return resp

    except Exception as e:
        return jsonify({"error": str(e)}), 500
