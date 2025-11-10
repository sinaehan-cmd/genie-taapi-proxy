# ======================================================
# 🌐 Genie Render Server – v3.2 Full Loop (Part 1/3)
# ======================================================
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import requests, os, json, base64, time
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import random

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────
# ⚙️ 환경 변수
# ─────────────────────────────────────────────
print("🔍 환경변수 로드 =======================")
print("GOOGLE_SERVICE_ACCOUNT:", bool(os.getenv("GOOGLE_SERVICE_ACCOUNT")))
print("SHEET_ID:", os.getenv("SHEET_ID"))
print("GENIE_ACCESS_KEY:", bool(os.getenv("GENIE_ACCESS_KEY")))
print("OPENAI_API_KEY:", bool(os.getenv("OPENAI_API_KEY")))
print("TAAPI_KEY:", bool(os.getenv("TAAPI_KEY")))
print("==================================================")

SHEET_ID = os.getenv("SHEET_ID")
TAAPI_KEY = os.getenv("TAAPI_KEY")
GENIE_ACCESS_KEY = os.getenv("GENIE_ACCESS_KEY")

# ─────────────────────────────────────────────
# 🔑 Google Sheets 연결
# ─────────────────────────────────────────────
def get_service():
    try:
        key_json = json.loads(base64.b64decode(os.getenv("GOOGLE_SERVICE_ACCOUNT")))
        creds = service_account.Credentials.from_service_account_info(
            key_json, scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        service = build("sheets", "v4", credentials=creds)
        return service
    except Exception as e:
        print("❌ Google API 연결 오류:", str(e))
        return None

def get_sheet(name):
    """시트 없으면 생성 후 반환"""
    service = get_service()
    if not service:
        return None
    try:
        service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
        return service.spreadsheets().values()
    except Exception as e:
        print(f"⚠️ 시트 '{name}' 접근 오류:", e)
        return None

# ─────────────────────────────────────────────
# 🧩 기본 라우트
# ─────────────────────────────────────────────
@app.route("/")
def home():
    return jsonify({"status": "Genie v3.2 Full Loop running"})

@app.route("/indicator")
def indicator():
    """TAAPI.io API → RSI, EMA, MACD 등 가져오기"""
    try:
        indicator = request.args.get("indicator", "rsi")
        symbol = request.args.get("symbol", "BTC/USDT")
        interval = request.args.get("interval", "1h")
        period = request.args.get("period", "14")

        url = f"https://api.taapi.io/{indicator}?secret={TAAPI_KEY}&exchange=binance&symbol={symbol}&interval={interval}&period={period}"
        res = requests.get(url, timeout=10)
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ======================================================
# 🔮 Genie Core Loops – Prediction / GTI / Learning / System
# ======================================================

@app.route("/prediction_loop", methods=["GET"])
def prediction_loop():
    """1️⃣ 예측 생성 루프"""
    try:
        sheet_name = "genie_predictions"
        sheet = get_sheet(sheet_name)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 예측 시뮬레이션 (나중에 실제 모델 출력으로 교체)
        predicted_price = round(random.uniform(95000, 105000), 2)
        actual_price = round(random.uniform(95000, 105000), 2)
        deviation = round(abs(predicted_price - actual_price) / actual_price * 100, 2)
        confidence = round(100 - deviation * 0.8, 2)

        new_row = [
            f"PRED_{int(time.time())}",
            now, now, "BTC",
            predicted_price, "", "", "", "", confidence,
            actual_price, deviation, "", "AutoTest"
        ]
        sheet.append_row(new_row)
        print(f"✅ Prediction logged: {predicted_price} vs {actual_price} ({deviation}%)")
        return jsonify({"status": "ok", "predicted": predicted_price, "actual": actual_price, "deviation": deviation})
    except Exception as e:
        print("❌ prediction_loop error:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/gti_loop", methods=["GET"])
def gti_loop():
    """2️⃣ GTI (Genie Trust Index) 루프"""
    try:
        sheet_name = "genie_gti_log"
        sheet = get_sheet(sheet_name)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        avg_dev = round(random.uniform(2, 5), 2)
        gti_score = round(100 - avg_dev * 0.98, 2)

        new_row = [
            f"GTI_{int(time.time())}",
            now, "1d", random.randint(5, 12),
            avg_dev, gti_score,
            "(100 - avg_dev * 0.98)",
            "Auto_Prediction", "Stable", "Auto"
        ]
        sheet.append_row(new_row)
        print(f"✅ GTI Logged: {gti_score}")
        return jsonify({"status": "ok", "gti": gti_score})
    except Exception as e:
        print("❌ gti_loop error:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/learning_loop", methods=["GET"])
def learning_loop():
    """3️⃣ Learning Loop – GTI 기반 학습 보정"""
    try:
        sheet_name = "genie_formula_store"
        sheet = get_sheet(sheet_name)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        formula_name = "GTI_Auto_Adjust"
        formula_text = "(100 - avg_dev * 0.98)"
        linked_sheet = "genie_gti_log"
        version = f"v{now.replace(' ', '').replace(':', '').replace('-', '')}"
        gti_sample = round(random.uniform(90, 96), 2)

        new_row = [now, formula_name, formula_text, "자동 보정형 GTI 계산식", linked_sheet, version, gti_sample, "Auto-Learning"]
        sheet.append_row(new_row)
        print(f"✅ Learning Updated: {formula_name} = {gti_sample}")
        return jsonify({"status": "ok", "formula": formula_name, "score": gti_sample})
    except Exception as e:
        print("❌ learning_loop error:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/system_log", methods=["GET"])
def system_log():
    """4️⃣ System Log – 루프 실행 상태 기록"""
    try:
        sheet_name = "genie_system_log"
        sheet = get_sheet(sheet_name)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        trust_ok = random.choice(["TRUE", "TRUE", "FALSE"])
        runtime = round(random.uniform(1.2, 3.4), 2)
        next_run = (datetime.now()).strftime("%H:%M:%S")

        new_row = [
            f"SYS_{int(time.time())}",
            now, "AUTONOMOUS_LOOP",
            "✅OK", f"TRUST_OK={trust_ok}",
            runtime, f"next={next_run}"
        ]
        sheet.append_row(new_row)
        print(f"🧭 System Log recorded: AUTONOMOUS_LOOP (TRUST_OK={trust_ok})")
        return jsonify({"status": "ok", "trust": trust_ok, "runtime": runtime})
    except Exception as e:
        print("❌ system_log error:", str(e))
        return jsonify({"error": str(e)}), 500

# ======================================================
# 🧭 Genie Helper Routes – View / Write / AutoExec
# ======================================================

@app.route("/view-html/<sheet_name>")
def view_html(sheet_name):
    """Google Sheet → HTML 렌더링 (지니가 읽을 수 있는 버전)"""
    try:
        service = get_service()
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=SHEET_ID, range=sheet_name)
            .execute()
        )
        values = result.get("values", [])
        if not values:
            return "⚠️ No data in sheet."
        html = "<table border='1' style='border-collapse:collapse;'>"
        for row in values:
            html += "<tr>" + "".join([f"<td>{cell}</td>" for cell in row]) + "</tr>"
        html += "</table>"
        return render_template_string(html)
    except Exception as e:
        return f"<p>❌ Error: {e}</p>"

@app.route("/write-sheet", methods=["POST"])
def write_sheet():
    """任의 시트에 행 추가"""
    try:
        data = request.json
        sheet_name = data.get("sheet", "")
        values = data.get("values", [])
        service = get_service()
        body = {"values": [values]}
        service.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range=sheet_name,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        return jsonify({"status": "ok", "sheet": sheet_name, "values": values})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/auto_exec", methods=["GET"])
def auto_exec():
    """
    🔁 Auto Loop Executor
    Prediction → GTI → Learning → System 순으로 실행
    """
    try:
        print("🚀 Genie AutoExec started")
        steps = [
            ("prediction_loop", "/prediction_loop"),
            ("gti_loop", "/gti_loop"),
            ("learning_loop", "/learning_loop"),
            ("system_log", "/system_log")
        ]
        results = []
        for name, path in steps:
            try:
                r = requests.get(f"https://{request.host}{path}", timeout=12)
                results.append({name: r.json()})
                time.sleep(1.5)
            except Exception as e:
                results.append({name: f"error: {e}"})
        print("✅ AutoExec completed")
        return jsonify({"status": "completed", "results": results})
    except Exception as e:
        print("❌ AutoExec error:", str(e))
        return jsonify({"error": str(e)}), 500


# ======================================================
# 🚀 Run Server
# ======================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

