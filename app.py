# -*- coding: utf-8 -*-
# ======================================================
# 🌐 Genie Render Server – Rebuild v3.1
# ======================================================

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests, os, json, base64
from datetime import datetime
from urllib.parse import unquote
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────
# ⚙️ Google Sheets 인증
# ─────────────────────────────────────────────
def get_sheets_service(write=False):
    raw_env = os.getenv("GOOGLE_SERVICE_ACCOUNT")
    if not raw_env:
        raise ValueError("❌ GOOGLE_SERVICE_ACCOUNT not set")
    try:
        creds_json = base64.b64decode(raw_env).decode()
    except Exception:
        creds_json = raw_env.replace("\\n", "\n")
    creds_dict = json.loads(creds_json)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"] if write else ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return build("sheets", "v4", credentials=credentials, cache_discovery=False)

# ─────────────────────────────────────────────
# 📈 Binance 가격 수집 함수
# ─────────────────────────────────────────────
def get_binance_price(symbol="BTCUSDT"):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    res = requests.get(url, timeout=10)
    return float(res.json()["price"])

# ─────────────────────────────────────────────
# 🌐 상태 확인
# ─────────────────────────────────────────────
@app.route("/test")
def test():
    return jsonify({
        "status": "✅ Genie Render Server Running (v3.1)",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# ─────────────────────────────────────────────
# 💰 가격 조회
# ─────────────────────────────────────────────
@app.route("/fetch_price")
def fetch_price():
    try:
        btc = get_binance_price("BTCUSDT")
        eth = get_binance_price("ETHUSDT")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return jsonify({"timestamp": now, "BTC_USDT": btc, "ETH_USDT": eth})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# ✍️ 가격 시트 기록
# ─────────────────────────────────────────────
@app.route("/price_write", methods=["POST"])
def price_write():
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403

        btc = get_binance_price("BTCUSDT")
        eth = get_binance_price("ETHUSDT")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        values = [[now, btc, eth]]

        service = get_sheets_service(write=True)
        service.spreadsheets().values().append(
            spreadsheetId=os.getenv("SHEET_ID"),
            range="genie_data_v5!A:C",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": values}
        ).execute()

        print(f"✅ Price written: BTC={btc}, ETH={eth}")
        return jsonify({"result": "success", "BTC": btc, "ETH": eth})
    except Exception as e:
        print("❌ price_write error:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 📜 git_log 기록
# ─────────────────────────────────────────────
@app.route("/git_log", methods=["POST"])
def git_log():
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403

        message = data.get("message", "")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [[now, "Genie_Server", message]]

        service = get_sheets_service(write=True)
        service.spreadsheets().values().append(
            spreadsheetId=os.getenv("SHEET_ID"),
            range="genie_git_log!A:C",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": row}
        ).execute()

        print(f"✅ git_log 기록 완료: {message}")
        return jsonify({"result": "logged", "message": message})
    except Exception as e:
        print("❌ git_log 오류:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 🏠 루트 경로
# ─────────────────────────────────────────────
@app.route("/")
def home():
    return jsonify({
        "status": "Genie Render Server ✅ (v3.1)",
        "routes": {
            "fetch_price": "/fetch_price",
            "price_write": "/price_write",
            "git_log": "/git_log"
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
