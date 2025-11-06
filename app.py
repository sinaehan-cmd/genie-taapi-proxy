# ======================================================
# 🧠 Genie System v2 – Full Integrated Version
# ======================================================
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import requests, os, json, base64, time
from datetime import datetime, timedelta
from urllib.parse import unquote
from google.oauth2 import service_account
from googleapiclient.discovery import build
from openai import OpenAI


app = Flask(__name__)

# ─────────────────────────────────────────────
# ⚙️ 환경 변수 로드
# ─────────────────────────────────────────────
GENIE_ACCESS_KEY = os.getenv("GENIE_ACCESS_KEY", "mySecretGenieKey_2025")
SHEET_ID = os.getenv("SHEET_ID")
RENDER_BASE_URL = os.getenv("RENDER_BASE_URL", "https://genie-taapi-proxy-1.onrender.com")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ─────────────────────────────────────────────
# 🧩 구글 시트 서비스 생성 함수
# ─────────────────────────────────────────────
def get_sheets_service(write=False):
    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT")
    if not creds_json:
        raise ValueError("Missing GOOGLE_SERVICE_ACCOUNT environment variable.")
    creds_dict = json.loads(base64.b64decode(creds_json))
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return build("sheets", "v4", credentials=creds)

# ─────────────────────────────────────────────
# 📡 Telegram 알림 전송 함수
# ─────────────────────────────────────────────
def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram config missing.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print("⚠️ Telegram send failed:", e)

# ─────────────────────────────────────────────
# 📊 Prediction Loop
# ─────────────────────────────────────────────
@app.route("/prediction_loop", methods=["POST"])
def prediction_loop():
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != GENIE_ACCESS_KEY:
            return jsonify({"error": "Invalid access key"}), 403

        # ✅ 예시: BTC 가격 수집 (TAAPI 연동 구조 유지)
        btc_price = 102000.0  # Placeholder – 실제 TAAPI 연동 코드 가능
        row_data = [[
            f"P01.{datetime.now().strftime('%Y-%m-%d-%H:%M')}",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "BTC",
            btc_price,
            60,
            56.0,
            "GTI=(100-AvgDev)",
            "Auto",
            "logged",
            "Genie System v2"
        ]]

        service = get_sheets_service(write=True)
        service.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range="genie_predictions!A:J",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": row_data}
        ).execute()

        print(f"✅ Prediction logged: {row_data[0][0]}")
        return jsonify({"result": "logged", "Prediction_ID": row_data[0][0]})
    except Exception as e:
        print("❌ prediction_loop error:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 📈 GTI Loop – Prediction Accuracy Evaluator (Safe Version)
# ─────────────────────────────────────────────
@app.route("/gti_loop", methods=["POST"])
def gti_loop():
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != GENIE_ACCESS_KEY:
            return jsonify({"error": "Invalid access key"}), 403

        service = get_sheets_service()
        pred = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range="genie_predictions!A:N").execute()
        pv = pred.get("values", [])
        if len(pv) < 2:
            return jsonify({"error": "No prediction data"})

        headers = pv[0]
        last_preds = pv[-5:]
        deviations = []

        data_result = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range="genie_data_v5!A:Z").execute()
        dv = data_result.get("values", [])
        if len(dv) < 2:
            return jsonify({"error": "No market data"})

        dh = dv[0]
        ld = dv[-1]
        actual_str = str(ld[dh.index("BTC/USD")]).strip()
        if actual_str in ["", "값없음", "None", "nan", "NaN"]:
            raise ValueError("Invalid actual BTC/USD value")
        actual_price = float(actual_str)

        for p in last_preds:
            try:
                val_str = str(p[headers.index("Predicted_Price")]).strip()
                if val_str in ["", "None", "nan", "값없음"]:
                    continue
                pred_price = float(val_str)
                dev = abs(pred_price - actual_price) / actual_price * 100
                deviations.append(dev)
            except Exception as e:
                continue

        if not deviations:
            return jsonify({"error": "No valid deviations"})

        avg_dev = round(sum(deviations) / len(deviations), 2)
        gti_score = max(0, min(100, 100 - avg_dev))
        trend = "Stable" if avg_dev < 2 else "Volatile"

        gti_id = f"GTI.{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        row_data = [[
            gti_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "1h",
            len(deviations),
            avg_dev,
            gti_score,
            "GTI=(100-AvgDeviation)",
            "Last 5 Predictions",
            trend,
            "Auto"
        ]]
        write_service = get_sheets_service(write=True)
        write_service.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range="genie_gti_log!A:J",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": row_data}
        ).execute()

        print(f"✅ GTI Logged: {gti_id} (Score={gti_score}, AvgDev={avg_dev}%)")
        return jsonify({"result": "logged", "GTI_Score": gti_score})
    except Exception as e:
        print("❌ gti_loop error:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 🧠 Learning Loop Internal – GTI 기반 자기보정 루프
# ─────────────────────────────────────────────
@app.route("/learning_loop_internal", methods=["POST"])
def learning_loop_internal():
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != GENIE_ACCESS_KEY:
            return jsonify({"error": "Invalid access key"}), 403

        service = get_sheets_service()
        gti = service.spreadsheets().values().get(spreadsheetId=SHEET_ID, range="genie_gti_log!A:J").execute()
        gv = gti.get("values", [])
        if len(gv) < 2:
            return jsonify({"error": "No GTI data"})

        headers = gv[0]
        recent = gv[-5:]
        scores = []
        for r in recent:
            try:
                s = float(r[headers.index("GTI_Score")])
                scores.append(s)
            except:
                continue

        avg_gti = round(sum(scores) / len(scores), 2)
        learning_rate = round(min(0.05, (100 - avg_gti) / 2000), 4)
        alpha = round(1 + learning_rate, 4)
        version = f"v{datetime.now().strftime('%Y%m%d%H%M')}"

        write_service = get_sheets_service(write=True)
        row = [[
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Auto_Adjust",
            f"(100 - avg_dev * {alpha})",
            "자동보정식",
            "genie_gti_log",
            version,
            avg_gti,
            f'{{"alpha": {alpha}}}',
            "Auto",
            "Learning"
        ]]
        write_service.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range="genie_formula_store!A:J",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": row}
        ).execute()

        print(f"✅ Learning Complete: avg_GTI={avg_gti}, α={alpha}")
        return jsonify({
            "result": "learning_complete",
            "avg_GTI": avg_gti,
            "learning_rate": learning_rate,
            "updated_formulas": len(recent)
        })
    except Exception as e:
        print("❌ learning_loop_internal error:", e)
        return jsonify({"error": str(e)}), 500
# ─────────────────────────────────────────────
# 🧠 Genie Main Loop (Async Version v2.1)
# ─────────────────────────────────────────────
import threading, time, requests, os
from flask import jsonify, request

def run_full_cycle(base_url, headers, body):
    """백그라운드에서 전체 루프 실행"""
    try:
        print("🚀 Genie main loop started in background")

        # 1️⃣ Prediction Loop
        r1 = requests.post(f"{base_url}/prediction_loop", json=body, headers=headers, timeout=20)
        print("✅ prediction_loop:", r1.status_code, r1.text)

        time.sleep(5)

        # 2️⃣ GTI Loop
        r2 = requests.post(f"{base_url}/gti_loop", json=body, headers=headers, timeout=20)
        print("✅ gti_loop:", r2.status_code, r2.text)

        time.sleep(5)

        # 3️⃣ Learning Loop
        r3 = requests.post(f"{base_url}/learning_loop_internal", json=body, headers=headers, timeout=20)
        print("✅ learning_loop_internal:", r3.status_code, r3.text)

        print("🧠 Genie Main Loop completed successfully ✅")

    except Exception as e:
        print("❌ main_loop background error:", str(e))


@app.route("/main_loop", methods=["POST"])
def main_loop():
    """빠른 응답형 메인 루프 (Render Timeout 회피용)"""
    try:
        data = request.get_json(force=True)
        access_key = data.get("access_key")
        if access_key != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403

        base_url = os.getenv("RENDER_BASE_URL", "https://genie-taapi-proxy-1.onrender.com")
        headers = {"Content-Type": "application/json"}
        body = {"access_key": os.getenv("GENIE_ACCESS_KEY")}

        # 백그라운드에서 전체 루프 실행
        thread = threading.Thread(target=run_full_cycle, args=(base_url, headers, body))
        thread.daemon = True
        thread.start()

        # 즉시 응답 반환 (Render Timeout 방지)
        return jsonify({
            "status": "processing_started",
            "message": "🧠 Genie main loop running in background",
            "note": "check logs or sheets for progress"
        })

    except Exception as e:
        print("❌ main_loop error:", e)
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# 🧾 시스템 헬스체크
# ─────────────────────────────────────────────
@app.route("/system_log", methods=["GET"])
def system_log():
    return jsonify({"status": "OK", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

# ─────────────────────────────────────────────
# 🛠️ 앱 실행
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
