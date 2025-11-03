from flask import Flask, jsonify, request, render_template_string
import requests
import os
import json
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

# === 환경변수 디버깅 ===
print("🔍 환경변수 로드 점검 시작 =======================")
print("GOOGLE_SERVICE_ACCOUNT 존재 여부:", bool(os.getenv("GOOGLE_SERVICE_ACCOUNT")))
print("SHEET_ID:", os.getenv("SHEET_ID"))
print("SHEET_NAME:", os.getenv("SHEET_NAME"))
print("==================================================")

# === TAAPI.io API 설정 ===
TAAPI_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjkwNGI5MzU4MDZmZjE2NTFlOGM1YTQ5IiwiaWF0IjoxNzYxOTIzNDU3LCJleHAiOjMzMjY2Mzg3NDU3fQ.g3Q3bM8pkKga6cgbhf9HDe99xAMPt6L4nRBrYybmDvk"
BASE_URL = "https://api.taapi.io"

# ─────────────────────────────────────────────
# 📘 Google Sheets Relay
# ─────────────────────────────────────────────
def get_sheets_service():
    raw_env = os.getenv("GOOGLE_SERVICE_ACCOUNT")
    if not raw_env:
        raise ValueError("❌ GOOGLE_SERVICE_ACCOUNT not set")

    # Base64 → JSON 디코딩
    try:
        creds_json = base64.b64decode(raw_env).decode()
    except Exception:
        creds_json = raw_env.replace('\\n', '\n')

    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=credentials)

# ─────────────────────────────────────────────
# 📗 시트 데이터 읽기 (JSON)
# ─────────────────────────────────────────────
@app.route("/read-sheet", methods=["GET"])
def read_sheet():
    try:
        sheet_id = os.environ.get("SHEET_ID")
        sheet_name = os.environ.get("SHEET_NAME", "지니_수집데이터_v5")

        if not sheet_id:
            raise ValueError("❌ No sheet_id detected from environment")

        service = get_sheets_service()
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range=f"{sheet_name}!A1:J")
            .execute()
        )
        values = result.get("values", [])
        return jsonify(values)
    except Exception as e:
        print("❌ Read Error:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 📘 시트에 쓰기 (POST)
# ─────────────────────────────────────────────
@app.route("/write-sheet", methods=["POST"])
def write_sheet():
    try:
        sheet_id = os.getenv("SHEET_ID")
        sheet_name = os.getenv("SHEET_NAME", "지니_수집데이터_v5")
        service = get_sheets_service()

        body = request.get_json()
        values = body.get("values")

        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption="USER_ENTERED",
            body={"values": values}
        ).execute()

        return jsonify({"status": "✅ Data written successfully"})
    except Exception as e:
        print("❌ Write Error:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 📊 HTML 테이블 뷰 (최근 7일만 표시)
# ─────────────────────────────────────────────
@app.route("/view-sheet")
def view_sheet():
    try:
        sheet_id = os.getenv("SHEET_ID")
        sheet_name = os.getenv("SHEET_NAME", "지니_수집데이터_v5")
        service = get_sheets_service()

        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range=f"{sheet_name}!A1:J")
            .execute()
        )
        values = result.get("values", [])

        if not values:
            return "<h3>❌ 시트에 데이터가 없습니다.</h3>"

        headers = values[0]
        rows = values[1:]

        # 🔹 최근 168행(=1시간 단위 7일치)만 출력
        if len(rows) > 168:
            rows = rows[-168:]

        # 🔹 날짜 범위 표시용 (첫 행~마지막 행)
        date_range = ""
        if rows:
            first_date = rows[0][0] if len(rows[0]) > 0 else ""
            last_date = rows[-1][0] if len(rows[-1]) > 0 else ""
            date_range = f"{first_date} ~ {last_date}"

        # 🔹 HTML 템플릿
        html = """
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="robots" content="index, follow">
            <title>Genie Data View</title>
            <style>
                body { font-family: 'Pretendard', sans-serif; background:#f8f9fa; padding:40px; }
                h2 { color:#333; margin-bottom:15px; }
                table { border-collapse: collapse; width:100%; background:white; box-shadow:0 2px 6px rgba(0,0,0,0.1); }
                th, td { border:1px solid #dee2e6; padding:8px 12px; text-align:center; }
                th { background:#343a40; color:#fff; }
                tr:nth-child(even){background:#f2f2f2;}
                caption { font-size:20px; font-weight:600; margin-bottom:10px; color:#333; }
            </style>
            <script>
                setTimeout(function(){ location.reload(); }, 600000); // 10분마다 새로고침
            </script>
        </head>
        <body>
            <h2>📊 Genie Google Sheets Live View (최근 7일)</h2>
            <p><b>📅 데이터 범위:</b> {{ date_range }}</p>
            <table>
                <thead>
                    <tr>
                        {% for header in headers %}
                            <th>{{ header }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for row in rows %}
                        <tr>
                            {% for cell in row %}
                                <td>{{ cell }}</td>
                            {% endfor %}
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </body>
        </html>
        """

        return render_template_string(html, headers=headers, rows=rows, date_range=date_range)

    except Exception as e:
        return f"<h3>❌ 오류 발생: {str(e)}</h3>"

# ─────────────────────────────────────────────
# 🌍 환경 체크
# ─────────────────────────────────────────────
@app.route("/env-check")
def env_check():
    return jsonify({
        "GOOGLE_SERVICE_ACCOUNT": bool(os.getenv("GOOGLE_SERVICE_ACCOUNT")),
        "SHEET_ID": os.getenv("SHEET_ID"),
        "SHEET_NAME": os.getenv("SHEET_NAME")
    })

@app.route('/robots.txt')
def robots_txt():
    return (
        "User-agent: *\nAllow: /",
        200,
        {'Content-Type': 'text/plain'}
    )

# ─────────────────────────────────────────────
# 🧠 기본 루트 & 인디케이터
# ─────────────────────────────────────────────
@app.route('/')
def home():
    return jsonify({"status": "Genie TAAPI Proxy Active ✅"})

@app.route('/indicator', methods=['GET'])
def get_indicator():
    symbol = request.args.get('symbol', 'BTC/USDT')
    exchange = request.args.get('exchange', 'binance')
    indicator = request.args.get('indicator', 'rsi')
    interval = request.args.get('interval', '1h')

    try:
        url = f"{BASE_URL}/{indicator}?secret={TAAPI_KEY}&exchange={exchange}&symbol={symbol}&interval={interval}"
        response = requests.get(url)
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 🏁 실행
# ─────────────────────────────────────────────
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
