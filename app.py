# -*- coding: utf-8 -*-
# ======================================================
# 🌐 Genie Render Server – Clean Integration Build v3.1
# ======================================================

from flask import Flask, jsonify, request
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

# === TAAPI.io API 설정 ===
TAAPI_KEY = os.getenv("TAAPI_KEY", "your_taapi_key_here")
BASE_URL = "https://api.taapi.io"

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
        creds_json = raw_env.replace("\\n", "\n")
    creds_dict = json.loads(creds_json)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    if not write:
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=scopes
    )
    return build("sheets", "v4", credentials=credentials, cache_discovery=False)

# ─────────────────────────────────────────────
# 🧠 지니 접근용 뷰 (단일 버전)
# ─────────────────────────────────────────────
@app.route("/view-readable/<path:sheet_name>")
def view_readable(sheet_name):
    """✅ 지니가 100% 읽을 수 있는 plain text 버전"""
    try:
        decoded = unquote(sheet_name)
        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=decoded
        ).execute()

        values = result.get("values", [])
        if not values:
            return f"❌ No data found in sheet: {decoded}", 404

        headers = values[0]
        rows = values[1:]
        text_lines = []
        for row in rows:
            entry = {headers[i]: (row[i] if i < len(row) else "") for i in range(len(headers))}
            text_lines.append(json.dumps(entry, ensure_ascii=False))
        text_output = "\n".join(text_lines)
        return app.response_class(response=text_output, status=200, mimetype="text/plain")
    except Exception as e:
        return f"❌ Error: {str(e)}", 500

# ─────────────────────────────────────────────
# ✅ 상태 확인 및 랜덤 트리거
# ─────────────────────────────────────────────
@app.route("/random.txt")
def random_txt():
    return "Genie_Access_OK\nThis file confirms safe static access.", 200, {"Content-Type": "text/plain"}

@app.route("/test")
def test():
    return jsonify({
        "status": "✅ Running (v3.1 Clean)",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# ─────────────────────────────────────────────
# 🎯 Indicator Endpoint (for TAAPI)
# ─────────────────────────────────────────────
@app.route("/indicator")
def indicator():
    """Return TAAPI indicator value as JSON (for Genie Sheets)."""
    try:
        indicator = request.args.get("indicator", "rsi")
        symbol = request.args.get("symbol", "BTC/USDT")
        interval = request.args.get("interval", "1h")
        period = request.args.get("period")
        params = {"secret": TAAPI_KEY, "exchange": "binance", "symbol": symbol, "interval": interval}
        if period:
            params["period"] = period
        url = f"{BASE_URL}/{indicator}"
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        if "value" in data:
            return jsonify({"indicator": indicator, "symbol": symbol, "interval": interval, "value": data["value"]})
        elif "valueMACD" in data:
            return jsonify({"indicator": indicator, "symbol": symbol, "interval": interval, "value": data["valueMACD"]})
        else:
            return jsonify({"error": "no_value", "raw": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
            body={"values": values},
        ).execute()
        print(f"✅ Data written to {sheet_name}: {values}")
        return jsonify({"result": "success", "sheet_name": sheet_name})
    except Exception as e:
        print("❌ write 오류:", e)
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# 🔁 Auto Loop – genie_data_v5 → genie_briefing_log
# ─────────────────────────────────────────────
@app.route("/auto_loop", methods=["POST"])
def auto_loop():
    """지니 Core 자동 브리핑 루프"""
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403
        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")

        def f(x): 
            try: return float(x)
            except: return 0.0

        src = service.spreadsheets().values().get(spreadsheetId=sheet_id, range="genie_data_v5!A:Z").execute()
        vals = src.get("values", [])
        if len(vals) < 2: 
            return jsonify({"error": "no data"})
        h, last = vals[0], vals[-1]

        def gv(c): return last[h.index(c)] if c in h else ""
        btc_rsi, btc_price, dom, mvrv, fng = f(gv("RSI(1h)")), f(gv("BTC/USD")), f(gv("Dominance(%)")), f(gv("MVRV_Z")), f(gv("FNG"))

        interp = "BULL_PREP" if btc_rsi > 60 and dom < 55 else "SIDEWAY"
        conf = max(0, min(100, 100 - abs(50 - btc_rsi)))
        ref = datetime.now().strftime("%Y%m%d%H%M%S")

        row = [[
            f"B01.{ref}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "BTC_USDT", btc_rsi, btc_price, dom, mvrv, interp, conf, 0, ref
        ]]

        ws = get_sheets_service(write=True)
        ws.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="genie_briefing_log!A:K",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": row}
        ).execute()
        print(f"✅ Auto loop logged: {row}")
        return jsonify({"result": "logged", "ref": ref})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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

        src = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range="genie_briefing_log!A:K"
        ).execute()
        vals = src.get("values", [])
        if len(vals) < 2:
            return jsonify({"error": "No briefing data"})

        h, last = vals[0], vals[-1]
        def val(c): return last[h.index(c)] if c in h else "0"

        btc_price = float(val("BTC_Price"))
        btc_rsi = float(val("BTC_RSI"))
        dominance = float(val("Dominance"))
        ref_id = val("Briefing_ID")

        prediction_time = datetime.now()
        target_time = prediction_time + timedelta(hours=1)

        predicted_price = round(btc_price * (1 + (btc_rsi - 50) / 1000), 2)
        predicted_rsi = round(btc_rsi * 0.98 + 1, 2)
        predicted_dom = round(dominance + (btc_rsi - 50) / 200, 2)
        confidence = max(0, min(100, 100 - abs(50 - btc_rsi)))

        prediction_id = f"P01.1.{prediction_time.strftime('%Y-%m-%d-%H:%M')}"
        row = [[
            prediction_id,
            prediction_time.strftime("%Y-%m-%d %H:%M:%S"),
            target_time.strftime("%Y-%m-%d %H:%M:%S"),
            "BTC_USDT",
            predicted_price,
            predicted_rsi,
            predicted_dom,
            "LinearDelta(v1.1)",
            "AUTO",
            confidence,
            "",
            "",
            ref_id,
            "Auto-predicted by Genie",
        ]]

        ws = get_sheets_service(write=True)
        ws.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="genie_predictions!A:N",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": row},
        ).execute()

        print(f"✅ Prediction logged: {prediction_id}")
        return jsonify({"result": "logged", "Prediction_ID": prediction_id})
    except Exception as e:
        print("❌ prediction_loop error:", e)
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# 📈 GTI Loop – Prediction Accuracy Evaluator
# ─────────────────────────────────────────────
@app.route("/gti_loop", methods=["POST"])
def gti_loop():
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403
        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")

        def safe_float(x):
            try:
                if x in ["", None, "값없음", "N/A", "-", "null"]:
                    return None
                return float(x)
            except Exception:
                return None

        pred = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range="genie_predictions!A:N"
        ).execute()
        pv = pred.get("values", [])
        if len(pv) < 2:
            return jsonify({"error": "No prediction data"})

        headers = pv[0]
        last_preds = pv[-5:]

        data_result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range="genie_data_v5!A:Z"
        ).execute()
        dv = data_result.get("values", [])
        if len(dv) < 2:
            return jsonify({"error": "No market data"})

        dh = dv[0]
        ld = dv[-1]
        actual_price = safe_float(ld[dh.index("BTC/USD")])
        if not actual_price:
            return jsonify({"result": "skipped", "reason": "no valid actual price"})

        deviations = []
        for p in last_preds:
            pred_price = safe_float(p[headers.index("Predicted_Price")])
            if pred_price:
                dev = abs(pred_price - actual_price) / actual_price * 100
                deviations.append(dev)
        if not deviations:
            return jsonify({"result": "skipped", "reason": "no valid deviations"})

        avg_dev = round(sum(deviations) / len(deviations), 2)
        gti_score = max(0, min(100, 100 - avg_dev))
        trend = "Stable" if avg_dev < 2 else "Volatile"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        gti_id = f"GTI.{now.replace(':','-').replace(' ','_')}"

        row = [[
            gti_id, now, "1h", len(deviations), avg_dev, gti_score,
            "GTI=(100-AvgDeviation)", "Last 5 Predictions", trend,
            "Auto-calculated by Genie"
        ]]

        ws = get_sheets_service(write=True)
        ws.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="genie_gti_log!A:J",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": row},
        ).execute()

        print(f"✅ GTI Logged: {gti_id} (Score = {gti_score}, AvgDev = {avg_dev}%)"_

# ─────────────────────────────────────────────
# 🌐 루트 경로
# ─────────────────────────────────────────────
@app.route("/")
def home():
    return jsonify({
        "status": "Genie Render Server ✅ (v3.1 Clean Build)",
        "routes": {
            "view": "/view-readable/<sheet_name>",
            "write": "/write",
            "auto_loop": "/auto_loop",
            "prediction_loop": "/prediction_loop",
            "gti_loop": "/gti_loop",
            "learning_loop": "/learning_loop",
            "system_log": "/system_log",
            "final_briefing": "/final_briefing"
        }
    })


# ─────────────────────────────────────────────
# 🚀 서버 실행
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
