# ─────────────────────────────────────────────
# 🧠 Genie Google Sheets Proxy (v2.3 – clean English sheets)
# ─────────────────────────────────────────────
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import requests, os, json, base64
from urllib.parse import unquote
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────
# ⚙️ 환경변수 로드
# ─────────────────────────────────────────────
print("🔍 환경변수 로드 =======================")
print("GOOGLE_SERVICE_ACCOUNT:", bool(os.getenv("GOOGLE_SERVICE_ACCOUNT")))
print("SHEET_ID:", os.getenv("SHEET_ID"))
print("GENIE_ACCESS_KEY:", bool(os.getenv("GENIE_ACCESS_KEY")))
print("==================================================")

# ─────────────────────────────────────────────
# 📗 Google Sheets 인증
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
# ✅ 서버 상태
# ─────────────────────────────────────────────
@app.route("/test")
def test():
    return jsonify({
        "status": "✅ Running",
        "sheet_id": os.getenv("SHEET_ID")
    })

# ─────────────────────────────────────────────
# 🌐 HTML 뷰
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
            <meta name="robots" content="index, follow">
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
# ✍️ 시트 쓰기
# ─────────────────────────────────────────────
@app.route("/write", methods=["POST"])
def write_data():
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403

        sheet_name = data.get("sheet_name")
        values = [data.get("values", [])]

        service = get_sheets_service(write=True)
        service.spreadsheets().values().append(
            spreadsheetId=os.getenv("SHEET_ID"),
            range=sheet_name,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": values}
        ).execute()

        print(f"✅ Data written to {sheet_name}: {values}")
        return jsonify({"result": "success", "sheet_name": sheet_name, "values": values})
    except Exception as e:
        print("❌ write 오류:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# robots.txt
# ─────────────────────────────────────────────
@app.route("/robots.txt")
def robots():
    return "User-agent: *\nAllow: /\n", 200, {"Content-Type": "text/plain"}

# ─────────────────────────────────────────────
# 루트
# ─────────────────────────────────────────────
@app.route("/")
def home():
    return jsonify({
        "status": "Genie Render Server ✅",
        "routes": {
            "view": "/view-html/<sheet_name>",
            "write": "/write",
            "test": "/test"
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
