# ======================================================
# 🌐 Genie Render Server – Stable Integration Build v3.1
# ======================================================
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import requests, os, json, base64
from urllib.parse import unquote
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from openai import OpenAI

# ─────────────────────────────────────────────
# ⚙️ Flask 기본 세팅
# ─────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────
# 🔑 환경 변수 로드 및 로그
# ─────────────────────────────────────────────
print("🔍 환경변수 로드 =======================")
print("GOOGLE_SERVICE_ACCOUNT:", bool(os.getenv("GOOGLE_SERVICE_ACCOUNT")))
print("SHEET_ID:", os.getenv("SHEET_ID"))
print("GENIE_ACCESS_KEY:", bool(os.getenv("GENIE_ACCESS_KEY")))

# ─────────────────────────────────────────────
# 📜 Google Sheets 인증
# ─────────────────────────────────────────────
def get_sheets_service(write=False):
    creds_json = os.getenv("GOOGLE_SERVICE_ACCOUNT")
    if not creds_json:
        raise Exception("❌ GOOGLE_SERVICE_ACCOUNT 환경변수 없음")
    creds_dict = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return build("sheets", "v4", credentials=creds)

# ─────────────────────────────────────────────
# 🧩 유틸리티 함수
# ─────────────────────────────────────────────
def fnum(v):
    try: return float(v)
    except: return None

@app.route("/")
def home():
    return jsonify({"status": "Genie Render v3.1", "result": "OK", "time": datetime.now().isoformat()})

# ─────────────────────────────────────────────
# 🔮 Prediction Loop – Genie 예측 자동 루프
# ─────────────────────────────────────────────
@app.route("/prediction_loop", methods=["POST"])
def prediction_loop():
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403
        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")
        src_range = "genie_briefing_log!A:K"
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=src_range).execute()
        values = result.get("values", [])
        if len(values) < 2:
            return jsonify({"error": "No briefing data"})
        headers = values[0]
        last = values[-1]
        def val(col): return last[headers.index(col)] if col in headers else ""
        btc_price = float(val("BTC_Price") or 0)
        btc_rsi = float(val("BTC_RSI") or 0)
        dominance = float(val("Dominance") or 0)
        ref_id = val("Briefing_ID")
        prediction_time = datetime.now()
        target_time = prediction_time + timedelta(hours=1)
        predicted_price = round(btc_price * (1 + (btc_rsi - 50) / 1000), 2)
        predicted_rsi = round(btc_rsi * 0.98 + 1, 2)
        predicted_dom = round(dominance + (btc_rsi - 50) / 200, 2)
        confidence = max(0, min(100, 100 - abs(50 - btc_rsi)))
        prediction_id = f"P01.1.{prediction_time.strftime('%Y-%m-%d-%H:%M')}"
        row_data = [[
            prediction_id, prediction_time.strftime("%Y-%m-%d %H:%M:%S"),
            target_time.strftime("%Y-%m-%d %H:%M:%S"), "BTC_USDT",
            predicted_price, predicted_rsi, predicted_dom,
            "LinearDelta(v1.1)", "AUTO", confidence, "", "", ref_id, "Auto-predicted by Genie"
        ]]
        write_service = get_sheets_service(write=True)
        write_service.spreadsheets().values().append(
            spreadsheetId=sheet_id, range="genie_predictions!A:N",
            valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS",
            body={"values": row_data},
        ).execute()
        print(f"✅ Prediction logged: {prediction_id}")
        return jsonify({"result": "logged", "Prediction_ID": prediction_id})
    except Exception as e:
        print("❌ prediction_loop error:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 📈 GTI Loop – 예측 정확도 평가
# ─────────────────────────────────────────────
@app.route("/gti_loop", methods=["POST"])
def gti_loop():
    try:
        s = get_sheets_service()
        sid = os.getenv("SHEET_ID")
        pred = s.spreadsheets().values().get(spreadsheetId=sid, range="genie_predictions!A:N").execute()
        pv = pred.get("values", [])
        if len(pv) < 2: return jsonify({"error": "No prediction data"})
        h = pv[0]; last5 = pv[-5:]
        data = s.spreadsheets().values().get(spreadsheetId=sid, range="genie_data_v5!A:Z").execute()
        dv = data.get("values", [])
        if len(dv) < 2: return jsonify({"error": "No market data"})
        dh, ld = dv[0], dv[-1]
        actual = fnum(ld[dh.index("BTC/USD")])
        if not actual: return jsonify({"result": "skipped", "reason": "no valid actual price"})
        devs = [abs(fnum(p[h.index("Predicted_Price")]) - actual) / actual * 100 for p in last5 if fnum(p[h.index("Predicted_Price")])]
        if not devs: return jsonify({"result": "skipped", "reason": "no valid deviations"})
        avg = round(sum(devs)/len(devs), 2); gti = max(0, min(100, 100 - avg))
        trend = "Stable" if avg < 2 else "Volatile"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        gid = f"GTI.{now.replace(':','-').replace(' ','_')}"
        row = [[gid, now, "1h", len(devs), avg, gti, "GTI=(100-AvgDev)", "Last 5", trend, "Auto by Genie"]]
        ws = get_sheets_service(write=True)
        ws.spreadsheets().values().append(spreadsheetId=sid, range="genie_gti_log!A:J",
            valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS",
            body={"values": row}).execute()
        return jsonify({"GTI": gti, "Deviation": avg})
    except Exception as e:
        print("❌ gti_loop error:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 🚀 서버 실행
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
