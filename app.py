from flask import Flask, jsonify, request
import requests
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

# === TAAPI.io 설정 ===
TAAPI_KEY = os.getenv("TAAPI_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjkwNGI5MzU4MDZmZjE2NTFlOGM1YTQ5IiwiaWF0IjoxNzYxOTIzNDU3LCJleHAiOjMzMjY2Mzg3NDU3fQ.g3Q3bM8pkKga6cgbhf9HDe99xAMPt6L4nRBrYybmDvk")
BASE_URL = "https://api.taapi.io"


# ────────────────────────────────
# 📘 Google Sheets (지니 ↔ 시트)
# ────────────────────────────────
def get_sheets_service():
    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT")
    if not creds_json:
        raise ValueError("❌ GOOGLE_SERVICE_ACCOUNT not set")

    creds_dict = json.loads(creds_json)
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=credentials, cache_discovery=False)


@app.route("/read-sheet", methods=["GET"])
def read_sheet():
    """Google Sheets에서 데이터 읽기"""
    try:
        sheet_id = os.getenv("SHEET_ID")
        sheet_name = os.getenv("SHEET_NAME", "지니_수집데이터_v5")
        service = get_sheets_service()

        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=sheet_id, range=f"{sheet_name}!A1:K")
            .execute()
        )
        values = result.get("values", [])
        if not values:
            return jsonify({"error": "⚠️ No data found in sheet"})
        return jsonify(values[-1])  # 최신 행만 반환
    except Exception as e:
        print("❌ Read Error:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/write-sheet", methods=["POST"])
def write_sheet():
    """Google Sheets에 데이터 쓰기"""
    try:
        sheet_id = os.getenv("SHEET_ID")
        sheet_name = os.getenv("SHEET_NAME", "지니_수집데이터_v5")
        service = get_sheets_service()

        body = request.get_json(force=True)
        values = body.get("values")

        if not values or not isinstance(values, list):
            return jsonify({"error": "⚠️ Invalid 'values' format"}), 400

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


# ────────────────────────────────
# 📊 TAAPI.io Proxy (기존)
# ────────────────────────────────
@app.route("/")
def home():
    return jsonify({"status": "Genie TAAPI Proxy Active ✅"})


@app.route("/indicator", methods=["GET"])
def get_indicator():
    symbol = request.args.get("symbol", "BTC/USDT")
    exchange = request.args.get("exchange", "binance")
    indicator = request.args.get("indicator", "rsi")
    interval = request.args.get("interval", "1h")

    try:
        url = f"{BASE_URL}/{indicator}?secret={TAAPI_KEY}&exchange={exchange}&symbol={symbol}&interval={interval}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        print("❌ Indicator Error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
