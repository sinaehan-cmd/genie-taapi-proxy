# -*- coding: utf-8 -*-
# ======================================================
# 🌐 Genie Render Server – Clean Integration Build v3.1 (Full Edition)
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
# 🧠 지니 접근용 뷰 (Plain Text)
# ─────────────────────────────────────────────
@app.route("/view-readable/<path:sheet_name>")
def view_readable(sheet_name):
    """✅ 지니가 100% 읽을 수 있는 plain text 버전"""
    try:
        decoded = unquote(sheet_name)
        s = get_sheets_service()
        sid = os.getenv("SHEET_ID")
        res = s.spreadsheets().values().get(spreadsheetId=sid, range=decoded).execute()
        vals = res.get("values", [])
        if not vals:
            return f"❌ No data found in sheet: {decoded}", 404
        h, rows = vals[0], vals[1:]
        lines = []
        for r in rows:
            e = {h[i]: (r[i] if i < len(r) else "") for i in range(len(h))}
            lines.append(json.dumps(e, ensure_ascii=False))
        out = "\n".join(lines)
        return app.response_class(response=out, status=200, mimetype="text/plain")
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
     try:
         ind = request.args.get("indicator", "rsi")
         sym = request.args.get("symbol", "BTC/USDT")
         interval = request.args.get("interval", "1h")
         period = request.args.get("period")
         params = {"secret": TAAPI_KEY, "exchange": "binance", "symbol": sym, "interval": interval}
         if period: params["period"] = period
         url = f"{BASE_URL}/{ind}"
         res = requests.get(url, params=params, timeout=10)
         data = res.json()
         if "value" in data:
             return jsonify({"indicator": ind, "symbol": sym, "interval": interval, "value": data["value"]})
         elif "valueMACD" in data:
             return jsonify({"indicator": ind, "symbol": sym, "interval": interval, "value": data["valueMACD"]})
         else:
             return jsonify({"error": "no_value", "raw": data}), 200
     except Exception as e:
         return jsonify({"error": str(e)}), 500

# ======================================================
# 📊 Genie Prediction & GTI (자동루프 / 학습 / 시트 기록)
# ======================================================

# ─────────────────────────────────────────────
# 📘 시트 쓰기 (행 추가)
# ─────────────────────────────────────────────
def append_to_sheet(sheet_name, values):
    try:
        s = get_sheets_service(write=True)
        sid = os.getenv("SHEET_ID")
        body = {"values": [values]}
        s.spreadsheets().values().append(
            spreadsheetId=sid,
            range=sheet_name,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()
        return True
    except Exception as e:
        print(f"❌ append_to_sheet Error: {e}")
        return False

# ─────────────────────────────────────────────
# 🧮 간단 예측 (RSI 기반 – Genie형 구조)
# ─────────────────────────────────────────────
@app.route("/predict")
def predict():
    """BTC RSI 기반 예측 예시"""
    try:
        symbol = request.args.get("symbol", "BTC/USDT")
        interval = request.args.get("interval", "1h")

        rsi_url = f"{BASE_URL}/rsi?secret={TAAPI_KEY}&exchange=binance&symbol={symbol}&interval={interval}"
        rsi_data = requests.get(rsi_url).json()
        rsi = rsi_data.get("value")

        if rsi is None:
            return jsonify({"error": "No RSI value"}), 400

        # 간단 예측 로직
        if rsi < 30:
            signal = "Strong Buy"
        elif 30 <= rsi < 45:
            signal = "Buy"
        elif 45 <= rsi < 55:
            signal = "Neutral"
        elif 55 <= rsi < 70:
            signal = "Sell"
        else:
            signal = "Strong Sell"

        result = {
            "symbol": symbol,
            "interval": interval,
            "rsi": round(rsi, 2),
            "signal": signal,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        append_to_sheet("genie_predictions", [
            result["timestamp"], symbol, interval, result["rsi"], result["signal"]
        ])

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 🧠 GTI 계산 예시
# ─────────────────────────────────────────────
@app.route("/gti")
def gti():
    """Genie Trust Index 계산 (Deviation 기반 샘플)"""
    try:
        predicted = float(request.args.get("predicted", 0))
        actual = float(request.args.get("actual", 0))
        deviation = abs(predicted - actual) / actual * 100 if actual != 0 else 0
        score = max(0, 100 - deviation)
        data = {
            "predicted": predicted,
            "actual": actual,
            "deviation(%)": round(deviation, 2),
            "GTI_Score": round(score, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        append_to_sheet("genie_gti_log", [
            data["timestamp"], predicted, actual, data["deviation(%)"], data["GTI_Score"]
        ])

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ======================================================
# 🪶 Genie Briefing & System Log (루프 / 기록)
# ======================================================

# ─────────────────────────────────────────────
# 🧾 브리핑 로그 기록 (자동 루프 예시)
# ─────────────────────────────────────────────
@app.route("/auto_loop")
def auto_loop():
    """자동 브리핑 루프 – RSI·Dominance·MVRV 계산"""
    try:
        # ─ 입력값
        symbol = request.args.get("symbol", "BTC/USDT")
        interval = request.args.get("interval", "1h")

        # ─ RSI
        rsi_url = f"{BASE_URL}/rsi?secret={TAAPI_KEY}&exchange=binance&symbol={symbol}&interval={interval}"
        rsi_val = requests.get(rsi_url).json().get("value", "값없음")

        # ─ Dominance (BTC.D, 근사치)
        dom_url = f"{BASE_URL}/dominance?secret={TAAPI_KEY}&exchange=binance&symbol={symbol}&interval={interval}"
        dom_val = requests.get(dom_url).json().get("value", "값없음")

        # ─ MVRV (근사치)
        mvrv_url = f"{BASE_URL}/mvrv?secret={TAAPI_KEY}&exchange=binance&symbol={symbol}&interval={interval}"
        mvrv_val = requests.get(mvrv_url).json().get("value", "값없음")

        # ─ 예측 기반 브리핑 텍스트 생성
        summary = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] RSI:{rsi_val}, DOM:{dom_val}, MVRV:{mvrv_val}"

        # ─ 시트에 기록
        append_to_sheet("genie_briefing_log", [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            symbol, interval, rsi_val, dom_val, mvrv_val, summary
        ])

        return jsonify({
            "status": "✅ Logged",
            "symbol": symbol,
            "rsi": rsi_val,
            "dominance": dom_val,
            "mvrv": mvrv_val,
            "summary": summary
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 🪵 시스템 로그용 엔드포인트
# ─────────────────────────────────────────────
@app.route("/system_log")
def system_log():
    """시스템 동작 기록"""
    try:
        message = request.args.get("message", "No message")
        append_to_sheet("genie_system_log", [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            message
        ])
        return jsonify({"logged": True, "message": message})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 🚀 앱 실행
# ─────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Genie Render Server v3.1 running on port {port}")
    app.run(host="0.0.0.0", port=port)

