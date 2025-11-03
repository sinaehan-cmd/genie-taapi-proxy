from flask import Flask, jsonify, request, render_template_string
import requests, os, json, base64
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

# ─────────────────────────────────────────────
# ⚙️ 환경 변수
# ─────────────────────────────────────────────
print("🔍 환경변수 로드 점검 =======================")
print("GOOGLE_SERVICE_ACCOUNT:", bool(os.getenv("GOOGLE_SERVICE_ACCOUNT")))
print("SHEET_ID:", os.getenv("SHEET_ID"))
print("GENIE_ACCESS_KEY:", bool(os.getenv("GENIE_ACCESS_KEY")))
print("==================================================")

GENIE_KEY = os.getenv("GENIE_ACCESS_KEY", "GENIE_DEFAULT_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ─────────────────────────────────────────────
# 🧠 Telegram 메시지 발송
# ─────────────────────────────────────────────
def send_telegram_message(text):
    """텔레그램으로 알림 전송"""
    try:
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            print("⚠️ Telegram 정보가 누락됨.")
            return
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
        requests.post(url, json=payload)
        print(f"✅ Telegram 전송 완료: {text}")
    except Exception as e:
        print(f"❌ Telegram 오류: {e}")

# ─────────────────────────────────────────────
# 📗 Google Sheets 연결
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
        creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=credentials)

# ─────────────────────────────────────────────
# 📘 다중 시트 쓰기 (POST)
# ─────────────────────────────────────────────
@app.route("/write-sheet", methods=["POST"])
def write_sheet():
    try:
        client_key = request.headers.get("X-GENIE-KEY", "")
        if client_key != GENIE_KEY:
            return jsonify({"error": "❌ Invalid GENIE key"}), 403

        body = request.get_json()
        target = body.get("target", "지니_수집데이터_v5")
        values = body.get("values")
        if not values:
            return jsonify({"error": "❌ No values provided"}), 400

        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")

        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=f"{target}!A1",
            valueInputOption="USER_ENTERED",
            body={"values": values}
        ).execute()

        # 🔥 불장 이벤트 감지 시 Telegram 발송
        joined = str(values).lower()
        if any(k in joined for k in ["불장", "급등", "급락", "폭락"]):
            send_telegram_message(f"🚀 <b>불장 이벤트 감지</b>\n📄 대상: {target}\n📊 데이터: {values}")

        return jsonify({"status": "✅ written", "target": target, "values": values})
    except Exception as e:
        send_telegram_message(f"❌ 시트 쓰기 오류: {e}")
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 📗 다중 시트 읽기 (GET)
# ─────────────────────────────────────────────
@app.route("/read-sheet", methods=["GET"])
def read_sheet():
    try:
        target = request.args.get("target", "지니_수집데이터_v5")
        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")

        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range=f"{target}!A1:Z")
            .execute()
        )
        return jsonify(result.get("values", []))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 🌐 HTML 보기 (시트명 선택)
# ─────────────────────────────────────────────
@app.route("/view-sheet/<target>")
def view_sheet(target):
    try:
        sheet_id = os.getenv("SHEET_ID")
        service = get_sheets_service()

        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range=f"{target}!A1:Z")
            .execute()
        )
        values = result.get("values", [])
        if not values:
            return f"<h3>❌ 시트 '{target}'에 데이터가 없습니다.</h3>"

        headers = values[0]
        rows = values[1:]
        if len(rows) > 168:
            rows = rows[-168:]
        date_range = f"{rows[0][0]} ~ {rows[-1][0]}" if rows else ""

        html = """
        <html><head><meta charset="utf-8"><meta name="robots" content="index, follow">
        <title>{{ target }} | Genie View</title>
        <style>
            body { font-family: Pretendard, sans-serif; background:#f8f9fa; padding:30px; }
            table { border-collapse: collapse; width:100%; background:white; }
            th, td { border:1px solid #ccc; padding:6px 10px; text-align:center; }
            th { background:#343a40; color:white; }
            tr:nth-child(even){background:#f2f2f2;}
        </style></head><body>
            <h2>📊 Genie Sheet: {{ target }}</h2>
            <p>📅 기간: {{ date_range }}</p>
            <table><thead><tr>
            {% for h in headers %}<th>{{ h }}</th>{% endfor %}
            </tr></thead><tbody>
            {% for row in rows %}<tr>{% for c in row %}<td>{{ c }}</td>{% endfor %}</tr>{% endfor %}
            </tbody></table></body></html>
        """
        return render_template_string(html, target=target, headers=headers, rows=rows, date_range=date_range)
    except Exception as e:
        return f"<h3>❌ 오류: {e}</h3>"

# ─────────────────────────────────────────────
# 📣 수동 Telegram 전송 엔드포인트
# ─────────────────────────────────────────────
@app.route("/send-alert", methods=["POST"])
def send_alert():
    body = request.get_json()
    msg = body.get("message", "⚠️ 기본 알림")
    send_telegram_message(msg)
    return jsonify({"status": "✅ Telegram sent", "message": msg})

# ─────────────────────────────────────────────
# 🌍 상태 점검
# ─────────────────────────────────────────────
@app.route("/env-check")
def env_check():
    return jsonify({
        "SHEET_ID": os.getenv("SHEET_ID"),
        "GENIE_ACCESS_KEY": bool(GENIE_KEY),
        "TELEGRAM_BOT_TOKEN": bool(TELEGRAM_BOT_TOKEN),
        "TELEGRAM_CHAT_ID": bool(TELEGRAM_CHAT_ID),
        "registered_sheets": [
            "지니_수집데이터_v5", "지니_브리핑로그", "지니_예측데이터",
            "지니_GTI로그", "지니_계산식저장소", "지니_시스템로그"
        ]
    })

# ─────────────────────────────────────────────
# 🏁 기본 루트
# ─────────────────────────────────────────────
@app.route("/")
def home():
    return jsonify({
        "status": "Genie Unified Proxy ✅",
        "routes": {
            "write": "/write-sheet (POST, target 지정)",
            "read": "/read-sheet?target=<시트명>",
            "view": "/view-sheet/<시트명> (HTML 보기)",
            "alert": "/send-alert (POST)"
        }
    })

# ─────────────────────────────────────────────
# 실행
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
