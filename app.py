# ─────────────────────────────────────────────
# 🧠 Genie Google Sheets Proxy (v2.2 – web-indexable edition)
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
# 🧩 한글 → 영문 알리아스 매핑 테이블
# ─────────────────────────────────────────────
SHEET_ALIAS = {
    "지니_수집데이터_v5": "genie_data_v5",
    "지니_브리핑로그": "genie_briefing_log",
    "지니_예측데이터": "genie_predictions",
    "지니_GTI로그": "genie_gti_log",
    "지니_계산식저장소": "genie_formula_store",
}

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
# ✅ 상태확인용 (Render 하트비트)
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
# 🌐 HTML 보기 (GPT 접근 허용)
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
            <meta name="robots" content="index, follow">
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
            <p style="margin-top:20px;color:gray;">Public view for Genie System – indexing allowed ✅</p>
        </body>
        </html>
        """
        return render_template_string(html)
    except Exception as e:
        print("❌ view-html 오류:", e)
        return f"<h3>오류 발생: {e}</h3>", 500

# ─────────────────────────────────────────────
# ✍️ 시트 쓰기 (Access Key 기반 인증)
# ─────────────────────────────────────────────
@app.route("/write", methods=["POST"])
def write_data():
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "❌ Invalid access key"}), 403

        raw_name = data.get("sheet_name")
        sheet_name = SHEET_ALIAS.get(raw_name, raw_name)
        values = [data.get("values", [])]

        service = get_sheets_service(write=True)
        service.spreadsheets().values().append(
            spreadsheetId=os.getenv("SHEET_ID"),
            range=sheet_name,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": values}
        ).execute()

        print(f"✅ [{raw_name}] → [{sheet_name}] 데이터 쓰기 완료:", values)
        return jsonify({
            "result": "✅ Write success",
            "sheet_name": raw_name,
            "alias_used": sheet_name,
            "values": values
        })

    except Exception as e:
        print("❌ write 오류:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 🪄 접근 신호 파일
# ─────────────────────────────────────────────
@app.route("/random.txt")
def random_txt():
    return "hello genie", 200, {"Content-Type": "text/plain"}

# ─────────────────────────────────────────────
# 🤖 robots.txt (모두 허용)
# ─────────────────────────────────────────────
@app.route("/robots.txt")
def robots():
    return (
        "User-agent: *\n"
        "Allow: /\n",
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
            "write": "/write",
            "random": "/random.txt",
            "robots": "/robots.txt"
        },
        "sheet_alias_mode": "한글 시트명 유지 + 영문 알리아스 자동 변환",
        "visibility": "GPT-accessible ✅"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
