# ======================================================
# 🌐 Genie Render Server – Stable Integration Build v3.0
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

# === TAAPI.io API 설정 ===
TAAPI_KEY = os.getenv("TAAPI_KEY", "your_taapi_key_here")
BASE_URL = "https://api.taapi.io"

# ─────────────────────────────────────────────
# ⚙️ 환경변수 점검 로그
# ─────────────────────────────────────────────
print("🔍 환경변수 로드 =======================")
print("GOOGLE_SERVICE_ACCOUNT:", bool(os.getenv("GOOGLE_SERVICE_ACCOUNT")))
print("SHEET_ID:", os.getenv("SHEET_ID"))
print("GENIE_ACCESS_KEY:", bool(os.getenv("GENIE_ACCESS_KEY")))
print("OPENAI_API_KEY:", bool(os.getenv("OPENAI_API_KEY")))
print("TAAPI_KEY:", bool(os.getenv("TAAPI_KEY")))
print("==================================================")

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
# 🪄 RANDOM 트리거 파일 (지니 접근 허용 신호)
# ─────────────────────────────────────────────
@app.route("/random.txt")
def random_txt():
    """
    ✅ GPT 접근 허용 신호용 랜덤 파일
    """
    random_text = """Genie_Access_OK
This file exists to mark this domain as static-content safe.
Updated: 2025-11-05
"""
    return random_text, 200, {"Content-Type": "text/plain"}

# ─────────────────────────────────────────────
# ✅ 서버 상태 확인용
# ─────────────────────────────────────────────
@app.route("/test")
def test():
    return jsonify({
        "status": "✅ Running (Stable v3.0)",
        "sheet_id": os.getenv("SHEET_ID"),
        "uptime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
# 🌐 HTML 뷰어 (for Genie System)
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
# 🌐 Smart JSON 뷰어 (Render 호환 + 지니 접근 허용 버전)
# ─────────────────────────────────────────────
@app.route("/view-json/<path:sheet_name>")
def view_sheet_json(sheet_name):
    """
    ✅ Google Sheets 데이터를 JSON으로 출력 (지니 읽기용)
    기본: 최근 200행
    옵션:
      ?limit=50   → 최근 50행
      ?since=2025-11-06 → 해당 날짜 이후만
      ?columns=Timestamp,BTC/USD,RSI(1h) → 필요한 열만
    """
    try:
        decoded = unquote(sheet_name)
        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")

        # 파라미터 처리
        limit = int(request.args.get("limit", 200))  # 🔸 기본 200행
        since = request.args.get("since")
        columns = request.args.get("columns")

        # 시트 데이터 가져오기
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=decoded
        ).execute()
        values = result.get("values", [])
        if not values or len(values) < 2:
            return app.response_class(
                response=json.dumps({"error": "No data found", "sheet": decoded}, ensure_ascii=False, indent=2),
                status=404,
                mimetype="text/html"  # ✅ Render에서 접근 허용되도록 HTML로 지정
            )

        headers = values[0]
        rows = []
        for row in values[1:]:
            entry = {}
            for i, header in enumerate(headers):
                if columns and header not in columns.split(","):
                    continue
                entry[header] = row[i] if i < len(row) else ""
            rows.append(entry)

        # 날짜 필터
        if since and "Timestamp" in headers:
            rows = [r for r in rows if r.get("Timestamp", "") >= since]

        # 최신 limit행만 반환
        rows = rows[-limit:]

        response = {
            "sheet": decoded,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "count": len(rows),
            "data": rows
        }

        print(f"✅ JSON view generated for {decoded} ({len(rows)} rows)")

        # 🔸 HTML 형태로 JSON 포장 (GPT/브라우저 접근 호환)
        html_wrapper = f"""
        <!DOCTYPE html>
        <html lang='en'>
        <head><meta charset='utf-8'><title>{decoded}</title></head>
        <body>
        <pre style='font-family: monospace; white-space: pre-wrap;'>{json.dumps(response, ensure_ascii=False, indent=2)}</pre>
        </body></html>
        """

        return app.response_class(
            response=html_wrapper,
            status=200,
            mimetype="text/html"
        )

    except Exception as e:
        print("❌ view-json error:", e)
        error_html = f"<h3>❌ 오류 발생:</h3><pre>{str(e)}</pre>"
        return app.response_class(response=error_html, status=500, mimetype="text/html")



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
        return jsonify({"result": "success", "sheet_name": sheet_name})
    except Exception as e:
        print("❌ write 오류:", e)
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# 🔁 Automation Loop – 지니 브리핑로그 구조화 버전
# ─────────────────────────────────────────────
@app.route("/auto_loop", methods=["POST"])
def auto_loop():
    """지니 Core 자동 브리핑 루프 (genie_data_v5 → genie_briefing_log)"""
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403

        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")

        def float_try(v, default=0.0):
            try:
                if v is None or str(v).strip() == "":
                    return default
                return float(v)
            except:
                return default

        def generate_briefing_id():
            now = datetime.now().strftime("%Y-%m-%d-%H:%M")
            import random
            return f"B01.2.{random.randint(1000,9999)}.{now}"

        def get_interpretation_code(rsi, dom, fng):
            try:
                if rsi >= 70: return "OVERHEAT"
                if rsi <= 30: return "OVERSOLD"
                if fng < 30 and rsi > 50: return "FEAR_BUY"
                if rsi > 60 and dom < 55: return "BULL_PREP"
                if rsi < 40 and dom > 55: return "BEAR_PRESSURE"
                return "SIDEWAY"
            except:
                return "UNKNOWN"

        src_range = "genie_data_v5!A:Z"
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=src_range
        ).execute()
        values = result.get("values", [])
        if not values or len(values) < 2:
            return jsonify({"error": "No data rows"})

        headers = values[0]
        last = values[-1]

        def get_val(col):
            if col in headers:
                idx = headers.index(col)
                return last[idx] if idx < len(last) else ""
            return ""

        btc_rsi = float_try(get_val("RSI(1h)"))
        btc_price = float_try(get_val("BTC/USD"))
        dominance = float_try(get_val("Dominance(%)"))
        mvrv_z = float_try(get_val("MVRV_Z"))
        fng_now = float_try(get_val("FNG"))
        market_code = get_val("MarketCode") or "BTC_USDT"

        briefing_id = generate_briefing_id()
        interpretation_code = get_interpretation_code(btc_rsi, dominance, fng_now)
        confidence = max(0, min(100, 100 - abs(50 - btc_rsi)))
        meta_score = round(
            (btc_rsi * 0.4 + (100 - abs(56 - dominance)) * 0.3 + (100 - abs(50 - mvrv_z)) * 0.3),
            2
        )
        reference_key = f"C01.1.{briefing_id.split('.')[2]}.{briefing_id.split('.')[3]}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        write_service = get_sheets_service(write=True)
        target_sheet = "genie_briefing_log"
        row_data = [[
            briefing_id, now, market_code, btc_rsi, btc_price,
            dominance, mvrv_z, interpretation_code, confidence, meta_score, reference_key
        ]]
        write_service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=f"{target_sheet}!A:K",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": row_data}
        ).execute()

        print(f"✅ Genie Briefing logged: {row_data}")
        return jsonify({
            "result": "logged",
            "Briefing_ID": briefing_id,
            "Interpretation": interpretation_code
        })
    except Exception as e:
        print("❌ auto_loop error:", e)
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
        src_range = "genie_briefing_log!A:K"
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=src_range
        ).execute()
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
            "LinearDelta(v1.1)", "AUTO", confidence,
            "", "", ref_id, "Auto-predicted by Genie"
        ]]

        write_service = get_sheets_service(write=True)
        write_service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="genie_predictions!A:N",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": row_data}
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

        pred = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range="genie_predictions!A:N"
        ).execute()
        pv = pred.get("values", [])
        if len(pv) < 2:
            return jsonify({"error": "No prediction data"})

        headers = pv[0]
        last_preds = pv[-5:]
        deviations = []

        data_result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range="genie_data_v5!A:Z"
        ).execute()
        dv = data_result.get("values", [])
        if len(dv) < 2:
            return jsonify({"error": "No market data"})

        dh = dv[0]
        ld = dv[-1]
        actual_price = float(ld[dh.index("BTC/USD")])

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

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        gti_id = f"GTI.{now.replace(':','-').replace(' ','_')}"
        row_data = [[
            gti_id, now, "1h", len(deviations), avg_dev, gti_score,
            "GTI=(100-AvgDeviation)", "Last 5 Predictions", trend,
            "Auto-calculated by Genie"
        ]]

        write_service = get_sheets_service(write=True)
        write_service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
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
# 🧠 Learning Loop v2.0 – GTI 기반 보정 루프 (최종본)
# ─────────────────────────────────────────────
@app.route("/learning_loop", methods=["POST"])
def learning_loop():
    """GTI 결과 기반으로 α(보정계수) 자동 조정 및 수식 저장"""
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403

        service = get_sheets_service()
        sheet_id = os.getenv("SHEET_ID")

        gti_result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range="genie_gti_log!A:J"
        ).execute()
        values = gti_result.get("values", [])
        if len(values) < 2:
            return jsonify({"error": "No GTI data"})

        headers = values[0]
        last = values[-1]
        def val(col): return last[headers.index(col)] if col in headers else ""
        current_gti = float(val("GTI_Score") or 0)
        avg_dev = float(val("Average_Deviation(%)") or 0)

        alpha = 1.0
        if current_gti < 85:
            alpha = round(1.0 + (85 - current_gti) / 200, 4)
        elif current_gti > 95:
            alpha = 0.98

        new_formula = f"(100 - avg_dev * {alpha})"
        version = f"v{datetime.now().strftime('%Y%m%d%H%M')}"
        confidence = round(min(100, 100 - abs(90 - current_gti)), 2)

        write_service = get_sheets_service(write=True)
        row = [[
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "GTI_Auto_Adjust",
            new_formula,
            "자동 보정형 GTI 계산식",
            "genie_gti_log",
            version,
            confidence,
            f'{{"alpha": {alpha}, "avg_dev": {avg_dev}}}',
            "Auto-Learning",
            "Genie System v2",
            "자동보정루프"
        ]]
        write_service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="genie_formula_store!A:K",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": row}
        ).execute()

        print(f"✅ Learning loop completed: GTI={current_gti}, α={alpha}")
        return jsonify({"result": "logged", "GTI": current_gti, "alpha": alpha, "version": version})
    except Exception as e:
        print("❌ learning_loop error:", e)
        return jsonify({"error": str(e)}), 500

# ─────────────────────────────────────────────
# 🧭 System Log Loop
# ─────────────────────────────────────────────
@app.route("/system_log", methods=["POST"])
def system_log():
    """Genie System 상태 기록 루프"""
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403

        service = get_sheets_service(write=True)
        sheet_id = os.getenv("SHEET_ID")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        module = data.get("module", "unknown")
        status = data.get("status", "OK")
        runtime = data.get("runtime", "")
        trust_ok = data.get("trust_ok", "TRUE")
        reason = data.get("reason", "")
        ref_id = data.get("ref_id", "")
        uptime = data.get("uptime", "")

        log_id = f"SYS.{now.replace(':','-').replace(' ','_')}"
        row_data = [[
            log_id, now, module, status, runtime,
            trust_ok, reason, ref_id, uptime
        ]]

        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="genie_system_log!A:I",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": row_data}
        ).execute()

        print(f"🧭 System Log recorded: {module} ({status}, TRUST_OK={trust_ok})")
        return jsonify({"result": "logged", "Log_ID": log_id})
    except Exception as e:
        print("❌ system_log error:", e)
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# 💬 Telegram Alert Sender
# ─────────────────────────────────────────────
def send_telegram_message(message: str):
    """텔레그램 메시지 전송 함수"""
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not token or not chat_id:
            print("⚠️ Telegram env not set")
            return {"error": "missing_token_or_chatid"}

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
        res = requests.post(url, data=payload, timeout=10)
        print("📤 Telegram Response:", res.status_code, res.text)
        return res.json()
    except Exception as e:
        print("❌ Telegram send error:", e)
        return {"error": str(e)}


# ─────────────────────────────────────────────
# 🚨 Alert Log Loop – 자동 텔레그램 전송 포함
# ─────────────────────────────────────────────
@app.route("/alert_log", methods=["POST"])
def alert_log():
    """알람 로그 저장 + 자동 텔레그램 발송"""
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403

        service = get_sheets_service(write=True)
        sheet_id = os.getenv("SHEET_ID")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        alert_id = f"ALERT.{now.replace(':','-').replace(' ','_')}"
        level = data.get("level", "INFO")
        message = data.get("message", "")
        source = data.get("source", "")
        category = data.get("category", "")
        ref = data.get("ref", "")

        row_data = [[alert_id, now, level, message, source, category, ref]]
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range="genie_alert_log!A:G",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": row_data}
        ).execute()

        print(f"🚨 Alert Log recorded: {message}")
        # 🔔 텔레그램 자동 전송
        tg_msg = f"🚨 <b>{level}</b> – {message}\n📍Source: {source}\n🕒 {now}"
        send_telegram_message(tg_msg)

        return jsonify({"result": "alert_logged", "Alert_ID": alert_id})
    except Exception as e:
        print("❌ alert_log error:", e)
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# 📡 /send – 외부 수동 테스트용
# ─────────────────────────────────────────────
@app.route("/send", methods=["POST"])
def send_message():
    """외부 POST로 텔레그램 알림 전송"""
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != os.getenv("GENIE_ACCESS_KEY"):
            return jsonify({"error": "Invalid access key"}), 403

        msg = data.get("message", "⚡ Test message from Genie System")
        result = send_telegram_message(msg)
        return jsonify({"status": "sent", "telegram_response": result})
    except Exception as e:
        print("❌ /send error:", e)
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# 🌐 루트 경로
# ─────────────────────────────────────────────
@app.route("/")
def home():
    return jsonify({
        "status": "Genie Render Server ✅ (v3.0)",
        "routes": {
            "view": "/view-html/<sheet_name>",
            "write": "/write",
            "auto_loop": "/auto_loop",
            "prediction_loop": "/prediction_loop",
            "gti_loop": "/gti_loop",
            "learning_loop": "/learning_loop",
            "system_log": "/system_log"
        }
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
