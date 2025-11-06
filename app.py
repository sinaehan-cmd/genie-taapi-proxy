# -*- coding: utf-8 -*-
# ======================================================
# 🌐 Genie Render Server – Stable Integration Build v3.0
# ======================================================

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import requests, os, json, base64
from urllib.parse import unquote
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from openai import OpenAI

# ─────────────────────────────────────────────
# ⚙️ Flask 기본 세팅
# ─────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

# === TAAPI.io API 설정 ===
TAAPI_KEY = os.getenv("TAAPI_KEY", "your_taapi_key_here")
BASE_URL = "https://api.taapi.io"

# ─────────────────────────────────────────────
# ⚙️ 환경변수 점검 로그
# ─────────────────────────────────────────────
print("🔍 환경변수 로드 =======================")
print("GOOGLE_SERVICE_ACCOUNT:", bool(os.getenv("GOOGLE_SERVICE_ACCOUNT")))
print("SHEET_ID:", os.getenv("SHEET_ID"))
print("GENIE_ACCESS_KEY:", bool(os.getenv("GENIE_ACCESS_KEY")))
print("OPENAI_API_KEY:", bool(os.getenv("OPENAI_API_KEY")))
print("TAAPI_KEY:", bool(os.getenv("TAAPI_KEY")))
print("==================================================")

# ─────────────────────────────────────────────
# 📗 Google Sheets 인증 함수
# ─────────────────────────────────────────────
def get_sheets_service(write=False):
    raw_env = os.getenv("GOOGLE_SERVICE_ACCOUNT")
    if not raw_env:
        raise ValueError("❌ GOOGLE_SERVICE_ACCOUNT not set")

    try:
        creds_json = base64.b64decode(raw_env).decode()
    except Exception:
        creds_json = raw_env.replace('\\n', '\n')

    creds_dict = json.loads(creds_json)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    if not write:
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    credentials = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=scopes
    )
    return build("sheets", "v4", credentials=credentials, cache_discovery=False)


# ─────────────────────────────────────────────
# 🪄 RANDOM 트리거 파일 (지니 접근 허용 신호)
# ─────────────────────────────────────────────
@app.route("/random.txt")
def random_txt():
    """✅ GPT 접근 허용 신호용 랜덤 파일"""
    random_text = """Genie_Access_OK
This file exists to mark this domain as static-content safe.
Updated: 2025-11-05"""
    return random_text, 200, {"Content-Type": "text/plain"}


# ─────────────────────────────────────────────
# ✅ 서버 상태 확인용
# ─────────────────────────────────────────────
@app.route("/test")
def test():
    return jsonify({
        "status": "✅ Running (Stable v3.0)",
        "sheet_id": os.getenv("SHEET_ID"),
        "uptime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


# ─────────────────────────────────────────────
# 🎯 Indicator Endpoint (for TAAPI)
# ─────────────────────────────────────────────
@app.route("/indicator")
def indicator():
    """Return TAAPI indicator value as JSON (for Genie Sheets)."""
    try:
        indicator = request.args.get("indicator", "rsi")
        symbol = request.args.get("symbol", "BTC/USDT")
        interval = request.args.get("interval", "1h")
        period = request.args.get("period")

        params = {
            "secret": TAAPI_KEY,
            "exchange": "binance",
            "symbol": symbol,
            "interval": interval
        }
        if period:
            params["period"] = period

        url = f"{BASE_URL}/{indicator}"
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        if "value" in data:
            return jsonify({
                "indicator": indicator,
                "symbol": symbol,
                "interval": interval,
                "value": data["value"]
            })
        elif "valueMACD" in data:
            return jsonify({
                "indicator": indicator,
                "symbol": symbol,
                "interval": interval,
                "value": data["valueMACD"]
            })
        else:
            return jsonify({"error": "no_value", "raw": data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# 🌐 HTML 뷰어 (for Genie System)
# ─────────────────────────────────────────────
@app.route("/view-html/<path:sheet_name>")
def view_sheet_html(sheet_name):
    try:
        decoded = unquote(sheet_name)
        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")

        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=decoded
        ).execute()

        values = result.get("values", [])
        if not values:
            return "<h3>No data found</h3>"

        table_html = "<table border='1' cellspacing='0' cellpadding='4'>"
        for row in values:
            table_html += "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"
        table_html += "</table>"

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="utf-8">
        <title>{decoded}</title>
        <style>
        body {{ font-family: 'Segoe UI', sans-serif; padding:20px; }}
        table {{ border-collapse:collapse; width:100%; max-width:900px; margin:auto; }}
        td {{ border:1px solid #ccc; padding:6px; font-size:13px; }}
        tr:nth-child(even) {{ background-color:#f9f9f9; }}
        </style>
        </head>
        <body>
        <h2>📘 {decoded}</h2>
        {table_html}
        <p style="color:gray;">Public view for Genie System ✅</p>
        </body>
        </html>
        """
        return render_template_string(html)

    except Exception as e:
        return f"<h3>오류: {e}</h3>", 500


# ─────────────────────────────────────────────
# 🌐 Smart JSON 뷰어 (Render 호환 + 지니 접근 허용 버전)
# ─────────────────────────────────────────────
@app.route("/view-json/<path:sheet_name>")
def view_sheet_json(sheet_name):
    """✅ Google Sheets 데이터를 JSON으로 출력 (지니 읽기용)"""
    try:
        decoded = unquote(sheet_name)
        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")

        limit = int(request.args.get("limit", 200))
        since = request.args.get("since")
        columns = request.args.get("columns")

        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=decoded
        ).execute()
        values = result.get("values", [])

        if not values or len(values) < 2:
            return app.response_class(
                response=json.dumps({"error": "No data found", "sheet": decoded}, ensure_ascii=False, indent=2),
                status=404,
                mimetype="text/html"
            )

        headers = values[0]
        rows = []
        for row in values[1:]:
            entry = {}
            for i, header in enumerate(headers):
                if columns and header not in columns.split(","):
                    continue
                entry[header] = row[i] if i < len(row) else ""
            rows.append(entry)

        if since and "Timestamp" in headers:
            rows = [r for r in rows if r.get("Timestamp", "") >= since]

        rows = rows[-limit:]

        response = {
            "sheet": decoded,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "count": len(rows),
            "data": rows
        }

        html_wrapper = f"""
        <!DOCTYPE html>
        <html lang='en'>
        <head><meta charset='utf-8'><title>{decoded}</title></head>
        <body>
        <pre style='font-family: monospace; white-space: pre-wrap;'>{json.dumps(response, ensure_ascii=False, indent=2)}</pre>
        </body></html>
        """
        return app.response_class(response=html_wrapper, status=200, mimetype="text/html")

    except Exception as e:
        print("❌ view-json error:", e)
        error_html = f"<h3>❌ 오류 발생:</h3><pre>{str(e)}</pre>"
        return app.response_class(response=error_html, status=500, mimetype="text/html")


# 이하 부분(📈 write, auto_loop, prediction_loop, gti_loop, learning_loop, system_log, home 등)은
# 원래 코드 그대로 유지해도 OK — 위처럼 UTF-8 헤더만 추가해도 인코딩 깨짐 문제는 완전히 해결돼.
