# ─────────────────────────────────────────────
# 🧠 Genie Google Sheets Proxy (v2.3 – clean English sheets)
# ─────────────────────────────────────────────
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import requests, os, json, base64
from urllib.parse import unquote
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────────
# ⚙️ 환경변수 로드
# ─────────────────────────────────────────────
print("🔍 환경변수 로드 =======================")
print("GOOGLE_SERVICE_ACCOUNT:", bool(os.getenv("GOOGLE_SERVICE_ACCOUNT")))
print("SHEET_ID:", os.getenv("SHEET_ID"))
print("GENIE_ACCESS_KEY:", bool(os.getenv("GENIE_ACCESS_KEY")))
print("🔑 OPENAI_API_KEY:", bool(os.getenv("OPENAI_API_KEY")))
print("==================================================")


# ─────────────────────────────────────────────
# 📗 Google Sheets 인증
# ─────────────────────────────────────────────
def get_sheets_service(write=False):
    raw_env = os.getenv("GOOGLE_SERVICE_ACCOUNT")
    if not raw_env:
        raise ValueError("❌ GOOGLE_SERVICE_ACCOUNT not set")
    try:
        creds_json = base64.b64decode(raw_env).decode()
    except Exception:
        creds_json = raw_env.replace('\\n', '\n')
    creds_dict = json.loads(creds_json)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    if not write:
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=scopes
    )
    return build("sheets", "v4", credentials=credentials, cache_discovery=False)

# ─────────────────────────────────────────────
# ✅ 서버 상태
# ─────────────────────────────────────────────
@app.route("/test")
def test():
    return jsonify({
        "status": "✅ Running",
        "sheet_id": os.getenv("SHEET_ID")
    })

# ─────────────────────────────────────────────
# 🌐 HTML 뷰
# ─────────────────────────────────────────────
@app.route("/view-html/<path:sheet_name>")
def view_sheet_html(sheet_name):
    try:
        decoded = unquote(sheet_name)
        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")

        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=decoded
        ).execute()
        values = result.get("values", [])
        if not values:
            return "<h3>No data found</h3>"

        table_html = "<table border='1' cellspacing='0' cellpadding='4'>"
        for row in values:
            table_html += "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"
        table_html += "</table>"

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="robots" content="index, follow">
            <title>{decoded}</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; padding:20px; }}
                table {{ border-collapse:collapse; width:100%; max-width:900px; margin:auto; }}
                td {{ border:1px solid #ccc; padding:6px; font-size:13px; }}
                tr:nth-child(even) {{ background-color:#f9f9f9; }}
            </style>
        </head>
        <body>
            <h2>📘 {decoded}</h2>
            {table_html}
            <p style="color:gray;">Public view for Genie System ✅</p>
        </body>
        </html>
        """
        return render_template_string(html)
    except Exception as e:
        return f"<h3>오류: {e}</h3>", 500

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
            body={"values": values}
        ).execute()

        print(f"✅ Data written to {sheet_name}: {values}")
        return jsonify({"result": "success", "sheet_name": sheet_name, "values": values})
    except Exception as e:
        print("❌ write 오류:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# robots.txt
# ─────────────────────────────────────────────
@app.route("/robots.txt")
def robots():
    return "User-agent: *\nAllow: /\n", 200, {"Content-Type": "text/plain"}

# ─────────────────────────────────────────────
# 🧠 Strategy Room – Genie Alert Writer
# ─────────────────────────────────────────────
@app.route("/strategy_write", methods=["POST"])
def strategy_write():
    """
    지니가 RSI, Dominance 등 조건을 감지하면
    genie_alert_log(지니_알람로그)에 자동 기록하는 엔드포인트
    """
    try:
        data = request.get_json(force=True)
        key = data.get("access_key")
        if key != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403

        rsi = float(data.get("RSI", 0))
        dominance = float(data.get("Dominance", 0))
        symbol = data.get("Symbol", "BTC")

        event, comment = None, ""
        if rsi >= 70:
            event, comment = "RSI_OVERHEAT", f"RSI 과열 ({rsi})"
        elif rsi <= 30:
            event, comment = "RSI_OVERSOLD", f"RSI 과매도 ({rsi})"
        elif dominance < 55:
            event, comment = "ALT_ROTATION", f"도미넌스 하락 ({dominance})"

        if not event:
            return jsonify({"result": "no_event", "RSI": rsi, "Dominance": dominance})

        # Google Sheets에 기록
        service = get_sheets_service(write=True)
        sheet_id = os.getenv("SHEET_ID")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        values = [[now, symbol, event, rsi, comment]]

        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="genie_alert_log",  # ✅ 시트명 (= 지니_알람로그)
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": values}
        ).execute()

        print(f"✅ Strategy event logged: {event} / {comment}")
        return jsonify({"result": "logged", "event": event, "RSI": rsi, "Dominance": dominance})

    except Exception as e:
        print("❌ strategy_write error:", e)
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# 🧠 Core Room – OpenAI API 기반 브리핑 쓰기
# ─────────────────────────────────────────────

@app.route("/core_write", methods=["POST"])
def core_write():
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403

        prompt = data.get("prompt", "Write a brief market summary for BTC and ETH.")
        sheet_name = data.get("sheet_name", "genie_briefing_log")

        # 🔑 OpenAI 호출 (v1.x 인터페이스)
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Genie, a concise market analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=200
        )

        summary = completion.choices[0].message.content.strip()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        values = [[now, prompt, summary]]

        # 📗 시트 기록
        service = get_sheets_service(write=True)
        service.spreadsheets().values().append(
            spreadsheetId=os.getenv("SHEET_ID"),
            range=sheet_name,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": values}
        ).execute()

        print(f"✅ Core summary logged to {sheet_name}")
        return jsonify({
            "result": "logged",
            "sheet_name": sheet_name,
            "summary": summary
        })

    except Exception as e:
        print("❌ core_write error:", e)
        return jsonify({"error": str(e)}), 500
        
# ─────────────────────────────────────────────
# 루트
# ─────────────────────────────────────────────
@app.route("/")
def home():
    return jsonify({
        "status": "Genie Render Server ✅",
        "routes": {
            "view": "/view-html/<sheet_name>",
            "write": "/write",
            "strategy_write": "/strategy_write",
            "core_write": "/core_write",
            "test": "/test"
        }
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
