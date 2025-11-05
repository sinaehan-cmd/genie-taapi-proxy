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

# === TAAPI.io API 설정 ===
TAAPI_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjkwNGI5MzU4MDZmZjE2NTFlOGM1YTQ5IiwiaWF0IjoxNzYyMjIyNTY1LCJleHAiOjMzMjY2Njg2NTY1fQ.VJ25E5hAGvSBYBSeDSX8FT7bW1EwhJY27VebneBrNPM"
BASE_URL = "https://api.taapi.io"


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
# ✅ TAAPI 확인
# ─────────────────────────────────────────────

@app.route("/taapi_test")
def taapi_test():
    """RSI 테스트 호출"""
    try:
        symbol = "BTC/USDT"
        interval = "1h"
        url = f"{BASE_URL}/rsi"
        params = {
            "secret": TAAPI_KEY,
            "exchange": "binance",
            "symbol": symbol,
            "interval": interval
        }

        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        print("📊 TAAPI response:", data)
        return jsonify(data)

    except Exception as e:
        print("❌ TAAPI test error:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 🎯 Indicator Endpoint (for Google Sheets)
# ─────────────────────────────────────────────
@app.route("/indicator")
def indicator():
    """Return TAAPI indicator value as JSON (for Genie Sheets)."""
    try:
        indicator = request.args.get("indicator", "rsi")
        symbol = request.args.get("symbol", "BTC/USDT")
        interval = request.args.get("interval", "1h")
        period = request.args.get("period")

        params = {
            "secret": TAAPI_KEY,
            "exchange": "binance",
            "symbol": symbol,
            "interval": interval
        }
        if period:
            params["period"] = period

        url = f"{BASE_URL}/{indicator}"
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        # 정규화된 출력
        if "value" in data:
            return jsonify({
                "indicator": indicator,
                "symbol": symbol,
                "interval": interval,
                "value": data["value"]
            })
        elif "valueMACD" in data:
            return jsonify({
                "indicator": indicator,
                "symbol": symbol,
                "interval": interval,
                "value": data["valueMACD"]
            })
        else:
            return jsonify({"error": "no_value", "raw": data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



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
# 🧠 Strategy Room – Genie Alert Writer (v2.1)
# ─────────────────────────────────────────────
@app.route("/strategy_write", methods=["POST"])
def strategy_write():
    """
    지니가 RSI, Dominance 등 조건을 감지하면
    genie_alert_log(지니_알람로그)에 자동 기록하는 엔드포인트
    - 시트 없을 경우 자동 생성 + 헤더 작성
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
        row_data = [[now, symbol, event, rsi, comment]]

        try:
            # ✅ 기존 시트에 바로 기록 시도
            service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range="genie_alert_log",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": row_data}
            ).execute()

        except Exception:
            # 🚀 시트 없을 경우 자동 생성
            sheet_def = {
                "requests": [{"addSheet": {"properties": {"title": "genie_alert_log"}}}]
            }
            try:
                service.spreadsheets().batchUpdate(
                    spreadsheetId=sheet_id, body=sheet_def
                ).execute()

                # 🧩 genie_alert_log 초기 헤더 자동 생성
                header_values = [[
                    "Timestamp",
                    "Symbol",
                    "Event",
                    "RSI",
                    "Comment"
                ]]
                service.spreadsheets().values().update(
                    spreadsheetId=sheet_id,
                    range="genie_alert_log!A1:E1",
                    valueInputOption="RAW",
                    body={"values": header_values}
                ).execute()
                print("🧩 genie_alert_log 초기 헤더 생성 완료 ✅")

                # 데이터 추가 재시도
                service.spreadsheets().values().append(
                    spreadsheetId=sheet_id,
                    range="genie_alert_log",
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                    body={"values": row_data}
                ).execute()

            except Exception as e:
                print("❌ Sheet creation or append failed:", e)
                return jsonify({"error": str(e)}), 500

        print(f"✅ Strategy event logged: {event} / {comment}")
        return jsonify({
            "result": "logged",
            "event": event,
            "RSI": rsi,
            "Dominance": dominance
        })

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
# 🔁 Automation Loop – 안정화 버전 v2.2 (GTI 구조 호환형)
# ─────────────────────────────────────────────
@app.route("/auto_loop", methods=["POST"])
def auto_loop():
    """
    🧠 Genie Core 자동 브리핑 루프 (1시간 주기 실행용)
    - genie_data_v5 시트에서 최신 데이터 읽기
    - GPT로 Interpretation 생성
    - GTI 호환 구조(Timestamp, MarketCode, BTC_RSI, BTC_Price, Dominance, MVRV_Z, Interpretation, Confidence, Comment)로 기록
    """
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403

        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")

        # ✅ 안전한 float 변환 함수 (빈칸·None 방어)
        def float_try(v, default=0.0):
            try:
                if v is None or str(v).strip() == "":
                    return default
                return float(v)
            except:
                return default

        # ① genie_data_v5 시트에서 최신 데이터 읽기
        src_range = "genie_data_v5!A:Z"
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=src_range
        ).execute()

        values = result.get("values", [])
        if not values or len(values) < 2:
            return jsonify({"error": "No data rows in genie_data_v5"})

        headers = values[0]
        last = values[-1]

        def get_val(col):
            if col in headers:
                idx = headers.index(col)
                return last[idx] if idx < len(last) else ""
            return ""

        btc_rsi = float_try(get_val("BTC_RSI"))
        btc_price = float_try(get_val("BTC_Price"))
        dominance = float_try(get_val("Dominance"))
        mvrv_z = float_try(get_val("MVRV_Z"))
        market_code = get_val("MarketCode") or "BTC_USDT"

        # ② GPT 호출 (Interpretation 생성)
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        prompt = (
            f"데이터를 기반으로 시장을 해석해줘.\n"
            f"RSI={btc_rsi}, Dominance={dominance}, MVRV_Z={mvrv_z}.\n"
            f"100자 이내로 간결하게 분석해줘."
        )

        gpt_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Genie, a precise market interpreter."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.4,
        )

        interpretation = gpt_response.choices[0].message.content.strip()

        # ③ Confidence 계산 (간단 점수화)
        confidence = max(0, min(100, 100 - abs(50 - btc_rsi)))  # RSI 중심 기반 단순 신뢰도
        comment = "Auto-generated by Genie Core Loop"

        # ④ 시트에 기록 (자동 생성 포함)
        write_service = get_sheets_service(write=True)
        target_sheet = "genie_briefing_log"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row_data = [
            now,            # Timestamp
            market_code,    # MarketCode
            btc_rsi,        # BTC_RSI
            btc_price,      # BTC_Price
            dominance,      # Dominance
            mvrv_z,         # MVRV_Z
            interpretation, # Interpretation
            confidence,     # Confidence
            comment         # Comment
        ]

        try:
            write_service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=f"{target_sheet}!A:I",  # ✅ 명시적 A~I 범위
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [row_data]}
            ).execute()

        except Exception:
            # 시트 없을 경우 자동 생성 후 재시도
            sheet_def = {
                "requests": [{"addSheet": {"properties": {"title": target_sheet}}}]
            }
            try:
                write_service.spreadsheets().batchUpdate(
                    spreadsheetId=sheet_id, body=sheet_def
                ).execute()

                # 🧩 지니_브리핑로그 초기 헤더 자동 생성
                header_values = [[
                    "Timestamp",
                    "MarketCode",
                    "BTC_RSI",
                    "BTC_Price",
                    "Dominance",
                    "MVRV_Z",
                    "Interpretation",
                    "Confidence",
                    "Comment"
                ]]

                write_service.spreadsheets().values().update(
                    spreadsheetId=sheet_id,
                    range=f"{target_sheet}!A1:I1",
                    valueInputOption="RAW",
                    body={"values": header_values}
                ).execute()

                print("🧩 genie_briefing_log 초기 헤더 생성 완료 ✅")

                # ✅ 헤더 작성 후 데이터 추가
                write_service.spreadsheets().values().append(
                    spreadsheetId=sheet_id,
                    range=f"{target_sheet}!A:I",
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                    body={"values": [row_data]}
                ).execute()

            except Exception as e:
                print("❌ Sheet creation or append failed:", e)
                return jsonify({"error": str(e)}), 500

        print(f"✅ Auto loop logged → {target_sheet}: {row_data}")
        return jsonify({
            "result": "logged",
            "summary": interpretation,
            "confidence": confidence,
            "MarketCode": market_code
        })

    except Exception as e:
        print("❌ auto_loop error:", e)
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
