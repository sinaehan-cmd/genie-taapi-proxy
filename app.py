from flask import Flask, jsonify, request, render_template_string
import requests, os, json, base64
from urllib.parse import unquote
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

# ─────────────────────────────────────────────
# ⚙️ 환경변수 로드
# ─────────────────────────────────────────────
print("🔍 환경변수 로드 =======================")
print("GOOGLE_SERVICE_ACCOUNT:", bool(os.getenv("GOOGLE_SERVICE_ACCOUNT")))
print("SHEET_ID:", os.getenv("SHEET_ID"))
print("==================================================")

TAAPI_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjkwNGI5MzU4MDZmZjE2NTFlOGM1YTQ5IiwiaWF0IjoxNzYyMjIyNTY1LCJleHAiOjMzMjY2Njg2NTY1fQ.VJ25E5hAGvSBYBSeDSX8FT7bW1EwhJY27VebneBrNPM"
BASE_URL = "https://api.taapi.io"

# ─────────────────────────────────────────────
# 📗 Google Sheets 인증
# ─────────────────────────────────────────────
def get_sheets_service():
    raw_env = os.getenv("GOOGLE_SERVICE_ACCOUNT")
    if not raw_env:
        raise ValueError("❌ GOOGLE_SERVICE_ACCOUNT not set")
    try:
        creds_json = base64.b64decode(raw_env).decode()
    except Exception:
        creds_json = raw_env.replace('\\n', '\n')
    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    return build("sheets", "v4", credentials=credentials, cache_discovery=False)

# ─────────────────────────────────────────────
# ✅ 상태확인용 엔드포인트 (Render 하트비트)
# ─────────────────────────────────────────────
@app.route("/test")
def test():
    return jsonify({
        "status": "ok",
        "message": "✅ Genie Proxy is running!",
        "note": "서버 정상 작동 중입니다."
    })

# ─────────────────────────────────────────────
# 📜 시트 목록 반환
# ─────────────────────────────────────────────
@app.route("/sheets-list")
def list_sheets():
    try:
        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")
        metadata = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = [s["properties"]["title"] for s in metadata["sheets"]]
        urls = [f"{request.host_url}view-html/{s}" for s in sheets]
        return jsonify({"sheets": sheets, "urls": urls})
    except Exception as e:
        print("❌ sheets-list 오류:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 🌐 HTML 보기 (지니 전용)
# ─────────────────────────────────────────────
@app.route("/view-html/<path:sheet_name>")
def view_sheet_html(sheet_name):
    try:
        decoded_name = unquote(sheet_name)
        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=decoded_name
        ).execute()
        values = result.get("values", [])
        if not values:
            return "<h3>No data found</h3>"

        table_html = "<table border='1' cellspacing='0' cellpadding='4' style='border-collapse:collapse;'>"
        for row in values:
            table_html += "<tr>" + "".join([f"<td>{cell}</td>" for cell in row]) + "</tr>"
        table_html += "</table>"

        html = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="utf-8">
            <meta name="robots" content="noindex, follow">
            <title>{decoded_name}</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; padding: 20px; background: #fafafa; }}
                table {{ width: 100%; max-width: 900px; margin:auto; background: white; }}
                td {{ border: 1px solid #ddd; padding: 6px; font-size: 13px; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
            </style>
        </head>
        <body>
            <h2>📘 {decoded_name}</h2>
            {table_html}
            <p style="margin-top:20px;color:gray;">Private view for Genie System</p>
        </body>
        </html>
        """
        return render_template_string(html)
    except Exception as e:
        print("❌ view-html 오류:", e)
        return f"<h3>오류 발생: {e}</h3>", 500

# ─────────────────────────────────────────────
# 🪄 접근 신호 파일
# ─────────────────────────────────────────────
@app.route("/random.txt")
def random_txt():
    return "hello genie", 200, {"Content-Type": "text/plain"}

# ─────────────────────────────────────────────
# 🤖 robots.txt
# ─────────────────────────────────────────────
@app.route("/robots.txt")
def robots():
    return (
        "User-agent: *\n"
        "Disallow: /\n"
        "Allow: /random.txt\n"
        "Allow: /view-html/\n"
        "Allow: /sheets-list\n"
        "Allow: /test\n",
        200,
        {"Content-Type": "text/plain"},
    )

# ─────────────────────────────────────────────
# 🏁 루트
# ─────────────────────────────────────────────
@app.route("/")
def home():
    return jsonify({
        "status": "Genie Render Server ✅",
        "routes": {
            "test": "/test",
            "list_sheets": "/sheets-list",
            "view_html": "/view-html/<sheet_name>",
            "random": "/random.txt",
            "robots": "/robots.txt"
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
