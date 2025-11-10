# -*- coding: utf-8 -*-
# ======================================================
# 🌐 Genie Render Server – Final Safe Version v3.2
# ======================================================

from flask import Flask, jsonify, request, Response
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
        "status": "✅ Genie Render Server Running (v3.2)",
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
# 📘 View-HTML (지니 접근용, 안전버전)
# ─────────────────────────────────────────────
@app.route("/view-html/<path:sheet_name>")
def view_sheet_html(sheet_name):
    try:
        decoded = unquote(sheet_name)
        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=decoded).execute()
        values = result.get("values", [])
        if not values:
            return "<h3>No data found</h3>"

        table_html = "<table border='1' cellspacing='0' cellpadding='4'>" + "".join(
            "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in values
        ) + "</table>"

        html = f"""<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><title>{decoded}</title>
        <style>body{{font-family:'Segoe UI',sans-serif;padding:20px;}}table{{border-collapse:collapse;width:100%;max-width:900px;margin:auto;}}td{{border:1px solid #ccc;padding:6px;font-size:13px;}}tr:nth-child(even){{background-color:#f9f9f9;}}</style></head>
        <body><h2>📘 {decoded}</h2>{table_html}<p style='color:gray;'>Public view for Genie System ✅</p></body></html>"""

        response = Response(html, mimetype="text/html")
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    except Exception as e:
        return f"<h3>오류: {e}</h3>", 500

# ─────────────────────────────────────────────
# 🌐 View-JSON (지니 접근용, 안전버전)
# ─────────────────────────────────────────────
@app.route("/view-json/<path:sheet_name>")
def view_sheet_json(sheet_name):
    try:
        decoded = unquote(sheet_name)
        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")
        result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=decoded).execute()
        values = result.get("values", [])
        if not values:
            return jsonify({"error": "No data found", "sheet": decoded}), 404

        headers = values[0]
        rows = [dict(zip(headers, row)) for row in values[1:]]
        return jsonify({"sheet": decoded, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "count": len(rows), "data": rows})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 🏠 루트 경로
# ─────────────────────────────────────────────
@app.route("/")
def home():
    return jsonify({
        "status": "Genie Render Server ✅ (v3.2 Final Safe)",
        "routes": {
            "fetch_price": "/fetch_price",
            "price_write": "/price_write",
            "git_log": "/git_log",
            "view_html": "/view-html/<sheet_name>",
            "view_json": "/view-json/<sheet_name>",
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
