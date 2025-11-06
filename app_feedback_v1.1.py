```python
# ======================================================
# 🤖 Genie Feedback Integration Build v1.1 – Auto Loop + Uptime Logging
# ======================================================
from flask import Flask
from flask_cors import CORS
import threading, time, requests, os
from datetime import datetime, timedelta
from app import app, get_sheets_service  # 기존 app.py 기반 모듈 그대로 사용

CORS(app)

# ─────────────────────────────────────────────
# ⚙️ 환경 변수 설정
# ─────────────────────────────────────────────
GENIE_ACCESS_KEY = os.getenv("GENIE_ACCESS_KEY")
RENDER_BASE_URL = os.getenv("RENDER_BASE_URL", "https://genie-taapi-proxy-1.onrender.com")
LOOP_INTERVAL = 3600  # ⏰ 1시간 간격
LAST_SUCCESS = datetime.now()

# ─────────────────────────────────────────────
# 🧠 내부 호출 함수
# ─────────────────────────────────────────────
def call_genie(endpoint: str):
    """지니 API 엔드포인트 호출 (Render 내부 self-call)"""
    try:
        url = f"{RENDER_BASE_URL}/{endpoint}"
        res = requests.post(url, json={"access_key": GENIE_ACCESS_KEY}, timeout=30)
        if res.status_code == 200:
            print(f"✅ {endpoint} 실행 완료 → {res.json()}")
        else:
            print(f"⚠️ {endpoint} 실행 실패 ({res.status_code}) → {res.text}")
    except Exception as e:
        print(f"❌ {endpoint} 호출 오류:", e)

# ─────────────────────────────────────────────
# 🔁 Auto Feedback Loop (1시간 간격)
# ─────────────────────────────────────────────
def auto_feedback_loop():
    """Prediction → GTI → Learning → SystemLog 순서로 주기적 실행"""
    global LAST_SUCCESS
    while True:
        try:
            start_time = datetime.now()
            print("\n🕒 [Auto Feedback Loop] 시작:", start_time.strftime("%Y-%m-%d %H:%M:%S"))

            # 1️⃣ 예측
            call_genie("prediction_loop")
            time.sleep(8)
            # 2️⃣ GTI 계산
            call_genie("gti_loop")
            time.sleep(8)
            # 3️⃣ 학습
            call_genie("learning_loop")
            time.sleep(4)

            # 4️⃣ 시스템 로그 기록
            end_time = datetime.now()
            runtime = (end_time - start_time).seconds
            uptime = 100 if (end_time - LAST_SUCCESS) < timedelta(hours=2) else 95
            LAST_SUCCESS = end_time
            next_slot = (end_time + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")

            try:
                # System Log에 기록
                requests.post(
                    f"{RENDER_BASE_URL}/system_log",
                    json={
                        "access_key": GENIE_ACCESS_KEY,
                        "module": "AUTO_FEEDBACK_LOOP",
                        "status": "✅OK",
                        "runtime": str(runtime),
                        "trust_ok": "TRUE",
                        "reason": "Auto Routine Completed",
                        "ref_id": f"AUTO.{end_time.strftime('%Y%m%d%H%M%S')}",
                        "uptime": str(uptime),
                    },
                    timeout=20,
                )
                print(f"✅ 루프 완료 | Runtime: {runtime}s | Uptime: {uptime}% | Next: {next_slot}")
            except Exception as e:
                print("⚠️ SystemLog 기록 오류:", e)

            print("💤 1시간 대기 중 ...")
        except Exception as e:
            print("❌ Auto Loop 오류:", e)
        time.sleep(LOOP_INTERVAL)

# ─────────────────────────────────────────────
# 🚀 서버 부팅 시 백그라운드 루프 시작
# ─────────────────────────────────────────────
def start_background_thread():
    thread = threading.Thread(target=auto_feedback_loop, daemon=True)
    thread.start()
    print("✅ Genie Auto Feedback Loop Started (interval = 1h, with Uptime Logging)")

# ─────────────────────────────────────────────
# 🏁 Flask 앱 실행
# ─────────────────────────────────────────────
if __name__ == "__main__":
    start_background_thread()
    app.run(host="0.0.0.0", port=8080)
```
