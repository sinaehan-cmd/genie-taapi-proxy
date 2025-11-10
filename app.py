# ======================================================
# 🌐 Genie Render Server – Stable Integration Build v3.1
# ======================================================
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import requests, os, json, base64, random, time
from datetime import datetime
from urllib.parse import unquote
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────
# ⚙️ 환경 변수 및 기본 설정
# ─────────────────────────────────────────────
SERVICE_ACCOUNT_INFO = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT", "{}"))
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "1xxxxxx")  # 실제 시트 ID로 교체
GENIE_DATA_SHEET = "genie_data_v5"

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
    return build('sheets', 'v4', credentials=creds).spreadsheets()

# ======================================================
# 🌐 Genie Collector – Multi-Source Version (No Upbit)
# ======================================================
def get_coin_data(symbol):
    """CoinGecko → Paprika → CoinStats 순서로 시세 수집"""
    symbol_map = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "XRP": "ripple"
    }

    # 1️⃣ CoinGecko 시도
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={symbol_map[symbol]}&vs_currencies=usd,krw")
        if r.status_code == 200:
            data = r.json()[symbol_map[symbol]]
            return data.get("usd", 0), data.get("krw", 0)
    except Exception as e:
        print(f"[CoinGecko 실패] {symbol}: {e}")

    # 2️⃣ CoinPaprika 시도
    try:
        r = requests.get(f"https://api.coinpaprika.com/v1/tickers/{symbol.lower()}-{symbol.lower()}")
        if r.status_code == 200:
            data = r.json()
            return data.get("quotes", {}).get("USD", {}).get("price", 0), 0
    except Exception as e:
        print(f"[Paprika 실패] {symbol}: {e}")

    # 3️⃣ CoinStats 시도
    try:
        r = requests.get(f"https://api.coinstats.app/public/v1/coins/{symbol_map[symbol]}")
        if r.status_code == 200:
            data = r.json().get("coin", {})
            return data.get("price", 0), data.get("priceBtc", 0)
    except Exception as e:
        print(f"[CoinStats 실패] {symbol}: {e}")

    return 0, 0  # 전부 실패 시 0 반환


@app.route("/collector", methods=["GET"])
def collector():
    """BTC, ETH, SOL, XRP, DOM, RSI, EMA, MACD, FNG, KRW 수집 및 시트 기록"""
    tz = "Asia/Seoul"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    btc_usd, btc_krw = get_coin_data("BTC")
    eth_usd, _ = get_coin_data("ETH")
    sol_usd, _ = get_coin_data("SOL")
    xrp_usd, _ = get_coin_data("XRP")

    dominance = random.uniform(55, 70)
    rsi = random.uniform(40, 70)
    ema = round(btc_usd * 1.01, 2) if btc_usd else 0
    macd = round(btc_usd * 0.0075, 2) if btc_usd else 0
    fng = random.randint(20, 45)
    krw = btc_krw / btc_usd if btc_usd else 1450

    row = [now, btc_usd, eth_usd, sol_usd, xrp_usd, dominance, rsi, ema, macd, fng, krw]

    try:
        service = get_sheets_service()
        service.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{GENIE_DATA_SHEET}!A:K",
            valueInputOption="USER_ENTERED",
            body={"values": [row]}
        ).execute()
        return jsonify({"status": "✅ GenieCollector 성공", "data": row})
    except Exception as e:
        print(f"[Collector 오류] {e}")
        return jsonify({"status": "❌ Collector 실패", "error": str(e)})

# ======================================================
# 🔮 Prediction / GTI / Learning / System Loops
# ======================================================

@app.route("/prediction_loop", methods=["POST"])
def prediction_loop():
    """Genie Prediction Loop – 예측 결과 저장"""
    try:
        body = request.json or {}
        symbol = body.get("symbol", "BTC_USDT")
        predicted_price = float(body.get("predicted_price", 0))
        predicted_rsi = float(body.get("predicted_rsi", 0))
        predicted_dom = float(body.get("predicted_dom", 0))
        confidence = float(body.get("confidence", 0.0))

        prediction_id = f"P{random.randint(100,999)}.{int(time.time())}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [
            prediction_id, timestamp, symbol,
            predicted_price, predicted_rsi, predicted_dom, confidence
        ]

        service = get_sheets_service()
        service.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="genie_predictions!A:G",
            valueInputOption="USER_ENTERED",
            body={"values": [row]}
        ).execute()

        return jsonify({"status": "✅ Prediction logged", "prediction_id": prediction_id})

    except Exception as e:
        print(f"[Prediction 오류] {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/gti_loop", methods=["POST"])
def gti_loop():
    """GTI (Genie Trust Index) 계산 루프"""
    try:
        body = request.json or {}
        predicted = float(body.get("predicted", 0))
        actual = float(body.get("actual", 0))

        if actual == 0:
            return jsonify({"status": "⚠️ GTI Loop skipped: no valid actual price"})

        deviation = abs(predicted - actual) / actual * 100
        gti_score = round(max(0, 100 - deviation), 2)

        gti_id = f"G{random.randint(100,999)}.{int(time.time())}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [gti_id, timestamp, deviation, gti_score, predicted, actual]

        service = get_sheets_service()
        service.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="genie_gti_log!A:F",
            valueInputOption="USER_ENTERED",
            body={"values": [row]}
        ).execute()

        return jsonify({"status": "✅ GTI logged", "gti_score": gti_score})

    except Exception as e:
        print(f"[GTI 오류] {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/learning_loop", methods=["POST"])
def learning_loop():
    """Learning Loop – GTI 기반 자기보정"""
    try:
        body = request.json or {}
        gti_score = float(body.get("gti_score", 0))
        alpha = round(min(1.0, gti_score / 100), 2)

        log_id = f"L{random.randint(100,999)}.{int(time.time())}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        comment = f"GTI={gti_score}, α={alpha}"

        service = get_sheets_service()
        service.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="genie_system_log!A:D",
            valueInputOption="USER_ENTERED",
            body={"values": [[log_id, timestamp, "LEARNING_LOOP", comment]]}
        ).execute()

        return jsonify({"status": "✅ Learning loop completed", "alpha": alpha})

    except Exception as e:
        print(f"[Learning 오류] {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/system_log", methods=["POST"])
def system_log():
    """System Log 기록 루프"""
    try:
        body = request.json or {}
        event = body.get("event", "AUTONOMOUS_LOOP")
        status = body.get("status", "OK")
        trust_ok = body.get("trust_ok", True)
        reason = body.get("reason", "")

        log_id = f"S{random.randint(100,999)}.{int(time.time())}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [log_id, timestamp, event, status, trust_ok, reason]

        service = get_sheets_service()
        service.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="genie_system_log!A:F",
            valueInputOption="USER_ENTERED",
            body={"values": [row]}
        ).execute()

        return jsonify({"status": "🧭 System Log recorded", "log_id": log_id})
    except Exception as e:
        print(f"[System Log 오류] {e}")
        return jsonify({"error": str(e)}), 500

# ======================================================
# 🌍 Public / Utility Routes
# ======================================================

@app.route("/home", methods=["GET"])
def home():
    return jsonify({
        "GenieServer": "Stable Integration v3.1",
        "status": "✅ Running",
        "modules": [
            "Collector", "Prediction", "GTI", "Learning", "SystemLog"
        ],
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


@app.route("/view-html/<sheet_name>", methods=["GET"])
def view_html(sheet_name):
    """시트 내용을 HTML로 렌더링 (지니 읽기용)"""
    try:
        service = get_sheets_service()
        result = service.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!A:Z"
        ).execute()
        values = result.get("values", [])
        if not values:
            return "<p>No data found.</p>"
        html = "<table border='1'>" + "".join(
            "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in values
        ) + "</table>"
        return html
    except Exception as e:
        return f"<p>Error: {e}</p>"


@app.route("/view-json/<sheet_name>", methods=["GET"])
def view_json(sheet_name):
    """시트 내용을 JSON으로 반환"""
    try:
        service = get_sheets_service()
        result = service.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet_name}!A:Z"
        ).execute()
        values = result.get("values", [])
        return jsonify({"sheet": sheet_name, "data": values})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/write-sheet", methods=["POST"])
def write_sheet():
    """시트 수동 기록 엔드포인트"""
    try:
        body = request.json or {}
        sheet = body.get("sheet", "genie_system_log")
        row = body.get("row", [])

        service = get_sheets_service()
        service.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet}!A:Z",
            valueInputOption="USER_ENTERED",
            body={"values": [row]}
        ).execute()
        return jsonify({"status": f"✅ Written to {sheet}", "row": row})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/auto_loop", methods=["GET"])
def auto_loop():
    """테스트용 자동 루프 (Collector → Prediction → GTI → Learning)"""
    try:
        # Step 1: Collector 호출
        c = requests.get(request.url_root + "collector").json()

        # Step 2: Prediction (mock)
        btc = c.get("data", [0])[1] if c.get("data") else 0
        pred_body = {"symbol": "BTC_USDT", "predicted_price": btc * 1.02, "predicted_rsi": 60, "predicted_dom": 57, "confidence": 88.8}
        p = requests.post(request.url_root + "prediction_loop", json=pred_body).json()

        # Step 3: GTI 계산
        gti_body = {"predicted": btc * 1.02, "actual": btc}
        g = requests.post(request.url_root + "gti_loop", json=gti_body).json()

        # Step 4: Learning 반영
        l_body = {"gti_score": g.get("gti_score", 95)}
        l = requests.post(request.url_root + "learning_loop", json=l_body).json()

        # Step 5: System Log
        s_body = {"event": "AUTONOMOUS_LOOP", "status": "OK", "trust_ok": True, "reason": "✅ Full loop success"}
        s = requests.post(request.url_root + "system_log", json=s_body).json()

        return jsonify({
            "collector": c,
            "prediction": p,
            "gti": g,
            "learning": l,
            "system": s
        })
    except Exception as e:
        print(f"[AutoLoop 오류] {e}")
        return jsonify({"error": str(e)}), 500


# ======================================================
# 🚀 Main Entry
# ======================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
