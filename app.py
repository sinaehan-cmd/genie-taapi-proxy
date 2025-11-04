from flask import Flask, jsonify, request, render_template_string
import requests, os, json, base64
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

# ─────────────────────────────────────────────
# ⚙️ 환경변수 및 기본 설정
# ─────────────────────────────────────────────
print("🔍 환경변수 로드 =======================")
print("GOOGLE_SERVICE_ACCOUNT:", bool(os.getenv("GOOGLE_SERVICE_ACCOUNT")))
print("SHEET_ID:", os.getenv("SHEET_ID"))
print("==================================================")

# 🔹 여기에 너의 TAAPI 유료 키를 직접 넣어
TAAPI_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjkwNGI5MzU4MDZmZjE2NTFlOGM1YTQ5IiwiaWF0IjoxNzYyMjIyNTY1LCJleHAiOjMzMjY2Njg2NTY1fQ.VJ25E5hAGvSBYBSeDSX8FT7bW1EwhJY27VebneBrNPM"
BASE_URL = "https://api.taapi.io"

# ─────────────────────────────────────────────
# 🧠 Telegram (선택사항, 생략해도 무방)
# ─────────────────────────────────────────────
def send_telegram_message(text):
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(text)
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print("Telegram Error:", e)

# ─────────────────────────────────────────────
# 📗 Google Sheets (선택적 사용)
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
    return build("sheets", "v4", credentials=credentials, cache_discovery=False)

# ─────────────────────────────────────────────
# 📈 TAAPI.io Indicator API (시트 스크립트용)
# ─────────────────────────────────────────────
@app.route("/indicator", methods=["GET"])
def get_indicator():
    symbol = request.args.get("symbol", "BTC/USDT")
    exchange = request.args.get("exchange", "binance")
    indicator = request.args.get("indicator", "rsi")
    interval = request.args.get("interval", "1h")

    try:
        url = (
            f"{BASE_URL}/{indicator}"
            f"?secret={TAAPI_KEY}&exchange={exchange}"
            f"&symbol={symbol}&interval={interval}"
        )
        print(f"➡️ Requesting: {url[:100]}...")  # 로그에 일부만 표시
        response = requests.get(url, timeout=10)
        data = response.json()

        val = (
            data.get("value")
            or (data.get("result", {}).get("value") if isinstance(data.get("result"), dict) else None)
            or (data.get("data", {}).get("value") if isinstance(data.get("data"), dict) else None)
        )
        macd_val = (
            data.get("valueMACD")
            or (data.get("result", {}).get("valueMACD") if isinstance(data.get("result"), dict) else None)
        )

        return jsonify({
            "value": val,
            "valueMACD": macd_val,
            "timestamp": data.get("timestamp", ""),
            "symbol": symbol,
            "indicator": indicator,
            "interval": interval
        })
    except Exception as e:
        print("❌ Indicator Error:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 🏁 루트
# ─────────────────────────────────────────────
@app.route("/")
def home():
    return jsonify({
        "status": "Genie Proxy ✅",
        "routes": {
            "indicator": "/indicator?indicator=rsi&symbol=BTC/USDT&interval=1h"
        }
    })

# ─────────────────────────────────────────────
# 실행
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
