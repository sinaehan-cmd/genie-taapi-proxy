# ─────────────────────────────────────────────
# 🧠 Genie Google Sheets Proxy (v2.3 – clean English sheets)
# ─────────────────────────────────────────────
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import requests, os, json, base64
from urllib.parse import unquote
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
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
# 🔁 Automation Loop – 지니 브리핑로그 구조화 버전 v2.1
# ─────────────────────────────────────────────
@app.route("/auto_loop", methods=["POST"])
def auto_loop():
    """
    🧠 Genie Core 자동 브리핑 루프 (1시간 주기 실행용)
    - genie_data_v5 시트에서 최신 데이터 읽기
    - Interpretation_Code, Confidence, Meta_Score 계산 후
      genie_briefing_log 시트에 기록 (기준키/참조키 포함)
    """
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403

        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")

        # ✅ 안전한 float 변환 함수
        def float_try(v, default=0.0):
            try:
                if v is None or str(v).strip() == "":
                    return default
                return float(v)
            except:
                return default

        # ✅ 기준키 생성 함수
        import random, datetime
        def generate_briefing_id():
            now = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")
            unique = random.randint(1000, 9999)
            return f"B01.2.{unique}.{now}"

        # ✅ 코드형 해석 함수
        def get_interpretation_code(rsi, dom, fng):
            try:
                rsi, dom, fng = float(rsi), float(dom), float(fng)
                if rsi >= 70: return "OVERHEAT"
                if rsi <= 30: return "OVERSOLD"
                if fng < 30 and rsi > 50: return "FEAR_BUY"
                if rsi > 60 and dom < 55: return "BULL_PREP"
                if rsi < 40 and dom > 55: return "BEAR_PRESSURE"
                if 40 <= rsi <= 60 and 54 <= dom <= 57: return "SIDEWAY"
                return "ALT_ROTATION"
            except:
                return "UNKNOWN"

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

        # 🔍 데이터 추출
        btc_rsi = float_try(get_val("RSI(1h)"))
        btc_price = float_try(get_val("BTC/USD"))
        dominance = float_try(get_val("Dominance(%)"))
        mvrv_z = float_try(get_val("MVRV_Z"))
        fng_now = float_try(get_val("FNG"))
        market_code = get_val("MarketCode") or "BTC_USDT"

        # ✅ 기준키 및 코드 생성
        briefing_id = generate_briefing_id()
        interpretation_code = get_interpretation_code(btc_rsi, dominance, fng_now)
        confidence = max(0, min(100, 100 - abs(50 - btc_rsi)))
        meta_score = round(
            (btc_rsi * 0.4 + (100 - abs(56 - dominance)) * 0.3 + (100 - abs(50 - mvrv_z)) * 0.3),
            2
        )
        reference_key = f"C01.1.{briefing_id.split('.')[2]}.{briefing_id.split('.')[3]}"
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ✅ 시트에 기록
        write_service = get_sheets_service(write=True)
        target_sheet = "genie_briefing_log"
        row_data = [
            briefing_id,
            now,
            market_code,
            btc_rsi,
            btc_price,
            dominance,
            mvrv_z,
            interpretation_code,
            confidence,
            meta_score,
            reference_key
        ]

        try:
            write_service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=f"{target_sheet}!A:K",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [row_data]}
            ).execute()

        except Exception:
            # 🚀 시트 없을 경우 자동 생성 + 헤더 작성
            sheet_def = {
                "requests": [{"addSheet": {"properties": {"title": target_sheet}}}]
            }
            write_service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id, body=sheet_def
            ).execute()

            header_values = [[
                "Briefing_ID",
                "Timestamp",
                "MarketCode",
                "BTC_RSI",
                "BTC_Price",
                "Dominance",
                "MVRV_Z",
                "Interpretation_Code",
                "Confidence",
                "Meta_Score",
                "Reference_Key"
            ]]

            write_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"{target_sheet}!A1:K1",
                valueInputOption="RAW",
                body={"values": header_values}
            ).execute()

            write_service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=f"{target_sheet}!A:K",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [row_data]}
            ).execute()

        print(f"✅ Genie Briefing logged: {row_data}")
        return jsonify({
            "result": "logged",
            "Briefing_ID": briefing_id,
            "Interpretation_Code": interpretation_code,
            "Meta_Score": meta_score,
            "Confidence": confidence
        })

    except Exception as e:
        print("❌ auto_loop error:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 🔮 Prediction Loop – Genie 예측 자동 루프 v1.2 (GTI Auto-Trigger 포함)
# ─────────────────────────────────────────────
@app.route("/prediction_loop", methods=["POST"])
def prediction_loop():
    """
    🧠 Genie Prediction Loop
    - genie_briefing_log에서 최신 Briefing_ID 기반 예측 생성
    - genie_predictions 시트에 기록
    - 완료 후 gti_loop 자동 호출 (GTI 신뢰도 계산)
    """
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403

        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")

        # ────────────────────────────────
        # ① 최신 브리핑 로그 불러오기
        # ────────────────────────────────
        src_range = "genie_briefing_log!A:K"
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=src_range
        ).execute()
        values = result.get("values", [])
        if not values or len(values) < 2:
            return jsonify({"error": "No data rows in genie_briefing_log"})

        headers = values[0]
        last = values[-1]

        def get_val(col):
            if col in headers:
                idx = headers.index(col)
                return last[idx] if idx < len(last) else ""
            return ""

        # ────────────────────────────────
        # ② 데이터 추출
        # ────────────────────────────────
        btc_price = float(get_val("BTC_Price") or 0)
        btc_rsi = float(get_val("BTC_RSI") or 0)
        dominance = float(get_val("Dominance") or 0)
        ref_id = get_val("Briefing_ID")

        # ────────────────────────────────
        # ③ 예측 계산
        # ────────────────────────────────
        from datetime import datetime, timedelta
        prediction_time = datetime.now()
        target_time = prediction_time + timedelta(hours=1)
        predicted_price = round(btc_price * (1 + (btc_rsi - 50) / 1000), 2)
        predicted_rsi = round(btc_rsi * 0.98 + 1, 2)
        predicted_dom = round(dominance + (btc_rsi - 50) / 200, 2)
        confidence = max(0, min(100, 100 - abs(50 - btc_rsi)))

        prediction_id = f"P01.1.{prediction_time.strftime('%Y-%m-%d-%H:%M')}"
        interpretation_code = get_val("Interpretation_Code") or "UNKNOWN"

        # ────────────────────────────────
        # ④ 시트에 기록
        # ────────────────────────────────
        row_data = [[
            prediction_id,
            prediction_time.strftime("%Y-%m-%d %H:%M:%S"),
            target_time.strftime("%Y-%m-%d %H:%M:%S"),
            "BTC_USDT",
            predicted_price,
            predicted_rsi,
            predicted_dom,
            "LinearDelta(v1.1)",
            interpretation_code,
            confidence,
            "",  # Actual_Price
            "",  # Deviation(%)
            ref_id,
            "Auto-predicted by Genie"
        ]]

        write_service = get_sheets_service(write=True)
        target_sheet = "genie_predictions"
        try:
            write_service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=f"{target_sheet}!A:N",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": row_data}
            ).execute()
        except Exception:
            # 🚀 시트 없을 경우 자동 생성
            sheet_def = {"requests": [{"addSheet": {"properties": {"title": target_sheet}}}]}
            write_service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id, body=sheet_def
            ).execute()

            header_values = [[
                "Prediction_ID", "Prediction_Time", "Target_Time", "Symbol",
                "Predicted_Price", "Predicted_RSI", "Predicted_Dominance",
                "Formula", "Interpretation_Code", "Confidence",
                "Actual_Price", "Deviation(%)", "Reference_ID", "Comment"
            ]]
            write_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"{target_sheet}!A1:N1",
                valueInputOption="RAW",
                body={"values": header_values}
            ).execute()

            write_service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=f"{target_sheet}!A:N",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": row_data}
            ).execute()

        print(f"✅ Prediction logged: {prediction_id}")

        # ────────────────────────────────
        # ⑤ 예측 성공 후 GTI 루프 자동 호출
        # ────────────────────────────────
        try:
            auto_call_url = "https://genie-taapi-proxy-1.onrender.com/gti_loop"
            auto_headers = {"Content-Type": "application/json"}
            auto_payload = {"access_key": os.getenv("GENIE_ACCESS_KEY")}
            gti_res = requests.post(auto_call_url, headers=auto_headers, json=auto_payload, timeout=20)

            if gti_res.status_code == 200:
                print("🔁 GTI loop auto-triggered successfully.")
            else:
                print(f"⚠️ GTI auto-trigger failed: {gti_res.status_code}")

        except Exception as e:
            print(f"⚠️ GTI auto-trigger error: {e}")

        # ────────────────────────────────
        # ⑥ 결과 반환
        # ────────────────────────────────
        return jsonify({
            "result": "logged",
            "Prediction_ID": prediction_id
        })

    except Exception as e:
        print("❌ prediction_loop error:", e)
        return jsonify({"error": str(e)}), 500



# ─────────────────────────────────────────────
# ⚙️ System Log Writer + Auto Alert (v1.2)
# ─────────────────────────────────────────────
@app.route("/system_log_write", methods=["POST"])
def system_log_write():
    """
    지니 시스템 상태 자동 기록 모듈 (Auto Alert 포함)
    - auto_loop 등 주요 루프 실행 후 결과 기록
    - TRUST_OK=FALSE 3회 연속 감지 시 자동 경보 발송
    """
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403

        # 기본 입력값
        module = data.get("module", "auto_loop")
        status = data.get("status", "✅ SUCCESS")
        runtime = float(data.get("runtime", 0))
        trust_ok = data.get("trust_ok", True)
        reason = data.get("reason", "")
        ref_id = data.get("ref_id", "")
        uptime = data.get("uptime", "99.9%")
        next_slot = data.get("next_slot", "")

        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_id = f"SYS.1.{now.replace(':','-')}"

        row_data = [[
            log_id,
            now,
            module,
            status,
            runtime,
            str(trust_ok).upper(),
            reason,
            ref_id,
            uptime,
            next_slot
        ]]

        service = get_sheets_service(write=True)
        sheet_id = os.getenv("SHEET_ID")
        target_sheet = "genie_system_log"

        # ✅ 시트에 로그 추가
        try:
            service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=f"{target_sheet}!A:J",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": row_data}
            ).execute()
        except Exception:
            # 🚀 시트 없을 경우 자동 생성 + 헤더 작성
            sheet_def = {
                "requests": [{"addSheet": {"properties": {"title": target_sheet}}}]
            }
            service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id, body=sheet_def
            ).execute()

            header_values = [[
                "Log_ID", "Timestamp", "Module", "Status",
                "Runtime(sec)", "TRUST_OK", "Reason",
                "Ref_ID", "Uptime%", "Next_Slot"
            ]]
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"{target_sheet}!A1:J1",
                valueInputOption="RAW",
                body={"values": header_values}
            ).execute()

            service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=f"{target_sheet}!A:J",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": row_data}
            ).execute()

        print(f"✅ System log recorded: {status} / {runtime}s / TRUST={trust_ok}")

        # ─────────────────────────────────────────────
        # 🚨 연속 실패 감지 및 경보 발송
        # ─────────────────────────────────────────────
        def check_recent_trust_failures():
            try:
                result = service.spreadsheets().values().get(
                    spreadsheetId=sheet_id, range=f"{target_sheet}!A:J"
                ).execute()
                values = result.get("values", [])
                if len(values) < 4:  # 헤더 제외 최소 3행 필요
                    return False
                recent = [row[5].upper() for row in values[-3:]]  # TRUST_OK 열
                return all(v == "FALSE" for v in recent)
            except Exception as e:
                print("⚠️ check_recent_trust_failures error:", e)
                return False

        def send_system_alert(reason, ref_id=""):
            try:
                alert_message = (
                    f"⚠️ [Genie System Alert]\n"
                    f"연속 3회 신뢰 불가 상태 감지.\n"
                    f"이유: {reason}\n"
                    f"참조키: {ref_id}\n"
                    f"조치: 자동 예측 중지 및 진단 루프 진입."
                )
                # Telegram 예시 (선택사항)
                TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
                CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
                if TELEGRAM_TOKEN and CHAT_ID:
                    requests.post(
                        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                        json={"chat_id": CHAT_ID, "text": alert_message},
                        timeout=10
                    )
                print("🚨 System Alert Triggered:", alert_message)
            except Exception as e:
                print("❌ send_system_alert error:", e)

        # 🚨 조건 충족 시 경보 발송
        if not trust_ok and check_recent_trust_failures():
            send_system_alert(reason, ref_id)

    except Exception as e:
        print("❌ system_log_write error:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 📈 Genie GTI Loop – Prediction Accuracy Evaluator v1.0
# ─────────────────────────────────────────────
@app.route("/gti_loop", methods=["POST"])
def gti_loop():
    """
    Compare predicted vs actual prices and record Genie Trust Index (GTI)
    - Reads from genie_predictions & genie_data_v5
    - Calculates average deviation and GTI score
    - Logs result to genie_gti_log
    """
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403

        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")

        # ────────────────────────────────
        # ① Read prediction data
        # ────────────────────────────────
        pred_result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range="genie_predictions!A:N"
        ).execute()
        pred_values = pred_result.get("values", [])
        if len(pred_values) < 2:
            return jsonify({"error": "No prediction data"})

        headers = pred_values[0]
        last_preds = pred_values[-5:]  # 최근 5개 예측만 평가
        deviations = []

        # ────────────────────────────────
        # ② Load latest actual BTC price from genie_data_v5
        # ────────────────────────────────
        data_result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range="genie_data_v5!A:Z"
        ).execute()
        data_values = data_result.get("values", [])
        if len(data_values) < 2:
            return jsonify({"error": "No market data"})

        data_headers = data_values[0]
        last_data = data_values[-1]
        actual_price = float(last_data[data_headers.index("BTC/USD")])

        # ────────────────────────────────
        # ③ Calculate deviations
        # ────────────────────────────────
        for p in last_preds:
            try:
                pred_price = float(p[headers.index("Predicted_Price")])
                dev = abs(pred_price - actual_price) / actual_price * 100
                deviations.append(dev)
            except Exception:
                continue

        if not deviations:
            return jsonify({"error": "No valid deviations"})

        avg_dev = round(sum(deviations) / len(deviations), 2)
        gti_score = max(0, min(100, 100 - avg_dev))
        trend = "Stable" if avg_dev < 2 else "Volatile"

        # ────────────────────────────────
        # ④ Write GTI log
        # ────────────────────────────────
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        gti_id = f"GTI.{now.replace(':','-').replace(' ','_')}"
        row_data = [
            gti_id,
            now,
            "1h",
            len(deviations),
            avg_dev,
            gti_score,
            "GTI=(100-AvgDeviation)",
            "Last 5 Predictions",
            trend,
            "Auto-calculated by Genie"
        ]

        write_service = get_sheets_service(write=True)
        target_sheet = "genie_gti_log"

        try:
            write_service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=f"{target_sheet}!A:J",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [row_data]}
            ).execute()
        except Exception:
            # Create sheet if missing
            sheet_def = {"requests": [{"addSheet": {"properties": {"title": target_sheet}}}]}
            write_service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id, body=sheet_def
            ).execute()
            header_values = [[
                "GTI_ID",
                "Timestamp",
                "Evaluation_Period",
                "Sample_Count",
                "Average_Deviation(%)",
                "GTI_Score",
                "Formula",
                "Source_Predictions",
                "Trend",
                "Comment"
            ]]
            write_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f"{target_sheet}!A1:J1",
                valueInputOption="RAW",
                body={"values": header_values}
            ).execute()
            write_service.spreadsheets().values().append(
                spreadsheetId=sheet_id,
                range=f"{target_sheet}!A:J",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [row_data]}
            ).execute()

        print(f"✅ GTI Logged: {gti_id} (Score={gti_score}, AvgDev={avg_dev}%)")
        return jsonify({
            "result": "logged",
            "GTI_ID": gti_id,
            "GTI_Score": gti_score,
            "Average_Deviation(%)": avg_dev
        })

    except Exception as e:
        print("❌ gti_loop error:", e)
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
