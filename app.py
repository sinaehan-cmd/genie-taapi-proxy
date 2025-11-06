# ======================================================
# 🌐 Genie Proxy Integration Server (Rollback Stable)
# Version: v2025.11-rollback-stable
# ======================================================

from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os, requests, time, base64
from datetime import datetime

app = Flask(__name__)

# ─────────────────────────────────────────────
# ⚙️ 환경 변수 로드
# ─────────────────────────────────────────────
GENIE_ACCESS_KEY = os.getenv("GENIE_ACCESS_KEY")
TAAPI_SECRET = os.getenv("TAAPI_SECRET")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
RENDER_BASE_URL = os.getenv("RENDER_BASE_URL", "https://genie-taapi-proxy-1.onrender.com")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ─────────────────────────────────────────────
# 📡 Google Sheets 인증
# ─────────────────────────────────────────────
def get_sheets_service():
    creds_b64 = os.getenv("GOOGLE_SERVICE_ACCOUNT")
    creds_json = base64.b64decode(creds_b64).decode("utf-8")
    creds = service_account.Credentials.from_service_account_info(eval(creds_json))
    return build("sheets", "v4", credentials=creds)

# ─────────────────────────────────────────────
# 📩 Telegram 메시지 전송
# ─────────────────────────────────────────────
def send_telegram(message: str):
    try:
        if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
            return
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})
    except Exception as e:
        print("⚠️ Telegram Error:", e)

# ─────────────────────────────────────────────
# 📊 TAAPI 지표 API
# ─────────────────────────────────────────────
@app.route("/indicator")
def get_indicator():
    try:
        indicator = request.args.get("indicator")
        symbol = request.args.get("symbol", "BTC/USDT")
        interval = request.args.get("interval", "1h")
        period = request.args.get("period", "14")

        if not indicator or not TAAPI_SECRET:
            return jsonify({"error": "Missing parameters"}), 400

        url = f"https://api.taapi.io/{indicator}?secret={TAAPI_SECRET}&exchange=binance&symbol={symbol}&interval={interval}&period={period}"
        resp = requests.get(url)
        data = resp.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 🔮 Prediction Loop – genie_predictions
# ─────────────────────────────────────────────
@app.route("/prediction_loop", methods=["POST"])
def prediction_loop():
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != GENIE_ACCESS_KEY:
            return jsonify({"error": "Invalid access key"}), 403

        sheet = get_sheets_service()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 예측 데이터 샘플 (시트 구조 원복)
        pred_id = f"P01.{now.replace(':', '-').replace(' ', '-')}"
        row = [
            pred_id, now, now, "BTC_USDT", "102000",
            "54.7", "56.9", "LinearDelta(v1.1)",
            "AUTO", "95.1", "", "", "Genie System v2", "Auto-predicted by Genie"
        ]

        sheet.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="genie_predictions!A:N",
            valueInputOption="USER_ENTERED",
            body={"values": [row]}
        ).execute()

        print(f"✅ Prediction logged: {pred_id}")
        return jsonify({"Prediction_ID": pred_id, "result": "logged"})

    except Exception as e:
        print("❌ prediction_loop error:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 📈 GTI Loop – genie_gti_log
# ─────────────────────────────────────────────
@app.route("/gti_loop", methods=["POST"])
def gti_loop():
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != GENIE_ACCESS_KEY:
            return jsonify({"error": "Invalid access key"}), 403

        service = get_sheets_service()
        pred_values = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range="genie_predictions!A:N"
        ).execute().get("values", [])
        if len(pred_values) < 2:
            raise ValueError("No prediction data found")

        data_values = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range="genie_data_v5!A:J"
        ).execute().get("values", [])
        if len(data_values) < 2:
            raise ValueError("No market data found")

        headers = data_values[0]
        last_row = data_values[-1]
        actual_price_str = str(last_row[headers.index("BTC/USD")]).strip()

        if actual_price_str in ["", "값없음", "None", "nan", "NaN"]:
            raise ValueError("Invalid actual BTC/USD value")

        actual_price = float(actual_price_str)
        deviations = []

        for row in pred_values[-5:]:
            try:
                val_str = row[4].strip()
                if val_str in ["", "값없음", "None", "nan"]:
                    continue
                dev = abs(float(val_str) - actual_price) / actual_price * 100
                deviations.append(dev)
            except:
                continue

        avg_dev = round(sum(deviations) / len(deviations), 2) if deviations else 0
        gti_score = max(0, min(100, 100 - avg_dev))
        trend = "Stable" if avg_dev < 2 else "Volatile"

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        gti_id = f"GTI.{now.replace(':','-').replace(' ','_')}"
        log_row = [gti_id, now, "1h", len(deviations), avg_dev, gti_score, "GTI=(100-AvgDev)", trend, "Auto"]

        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="genie_gti_log!A:I",
            valueInputOption="USER_ENTERED",
            body={"values": [log_row]}
        ).execute()

        print(f"✅ GTI Logged: {gti_id} (Score={gti_score}, AvgDev={avg_dev}%)")
        return jsonify({"result": "logged", "GTI_Score": gti_score})
    except Exception as e:
        print("❌ gti_loop error:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 🧩 Learning Loop Internal
# ─────────────────────────────────────────────
@app.route("/learning_loop_internal", methods=["POST"])
def learning_loop_internal():
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != GENIE_ACCESS_KEY:
            return jsonify({"error": "Invalid access key"}), 403

        sheet = get_sheets_service()
        res = sheet.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range="genie_gti_log!A:I"
        ).execute()
        vals = res.get("values", [])[1:]

        gti_scores = [float(v[5]) for v in vals if len(v) > 5 and v[5].replace('.', '', 1).isdigit()]
        avg_gti = round(sum(gti_scores) / len(gti_scores), 2) if gti_scores else 0
        learning_rate = round(1 + (avg_gti / 1000), 4)

        print(f"✅ Learning Complete: avg_GTI={avg_gti}, α={learning_rate}")
        return jsonify({"result": "learning_complete", "avg_GTI": avg_gti, "learning_rate": learning_rate})
    except Exception as e:
        print("❌ learning_loop_internal error:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 🔁 Main Loop – Prediction → GTI → Learning
# ─────────────────────────────────────────────
@app.route("/main_loop", methods=["POST"])
def main_loop():
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != GENIE_ACCESS_KEY:
            return jsonify({"error": "Invalid access key"}), 403

        headers = {"Content-Type": "application/json"}
        body = {"access_key": GENIE_ACCESS_KEY}

        requests.post(f"{RENDER_BASE_URL}/prediction_loop", json=body, headers=headers)
        time.sleep(5)
        requests.post(f"{RENDER_BASE_URL}/gti_loop", json=body, headers=headers)
        time.sleep(5)
        requests.post(f"{RENDER_BASE_URL}/learning_loop_internal", json=body, headers=headers)

        send_telegram("📊 Genie main loop completed successfully.")
        return jsonify({
            "status": "processing_started",
            "message": "🧠 Genie main loop running in background",
            "note": "check logs or sheets for progress"
        })
    except Exception as e:
        print("❌ main_loop error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
