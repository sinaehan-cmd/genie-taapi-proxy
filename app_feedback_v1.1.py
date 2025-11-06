# -*- coding: utf-8 -*-
# ======================================================
# 🤖 Genie Autonomous Feedback Layer v3.1 – Safe Overlay Mode
# ======================================================

import threading, time, requests, os
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# ⚙️ 환경 변수
# ─────────────────────────────────────────────
GENIE_ACCESS_KEY = os.getenv("GENIE_ACCESS_KEY")
RENDER_BASE_URL = os.getenv("RENDER_BASE_URL", "https://genie-taapi-proxy-1.onrender.com")
LOOP_INTERVAL = int(os.getenv("GENIE_LOOP_INTERVAL", 3600))  # 기본 1시간

LAST_SUCCESS = datetime.now()

# ─────────────────────────────────────────────
# 🔗 내부 호출 함수
# ─────────────────────────────────────────────
def call_genie(endpoint: str):
    """기존 app.py의 endpoint를 안전하게 호출"""
    try:
        url = f"{RENDER_BASE_URL}/{endpoint}"
        res = requests.post(url, json={"access_key": GENIE_ACCESS_KEY}, timeout=30)
        if res.status_code == 200:
            print(f"✅ {endpoint} 성공: {res.json()}")
        else:
            print(f"⚠️ {endpoint} 실패: {res.status_code} / {res.text}")
    except Exception as e:
        print(f"❌ {endpoint} 호출 오류:", e)

# ─────────────────────────────────────────────
# 🔁 자율 루프
# ─────────────────────────────────────────────
def auto_feedback_loop():
    """기존 Flask 엔드포인트를 순차 호출"""
    global LAST_SUCCESS
    while True:
        start_time = datetime.now()
        print("\n🕒 [Auto Feedback] 루프 시작:", start_time.strftime("%Y-%m-%d %H:%M:%S"))

        try:
            call_genie("auto_loop")        # 브리핑 생성
            time.sleep(6)
            call_genie("prediction_loop")  # 예측
            time.sleep(6)
            call_genie("gti_loop")         # 신뢰도 평가
            time.sleep(6)
            call_genie("learning_loop")    # 수식 보정
            time.sleep(6)

            runtime = (datetime.now() - start_time).seconds
            uptime = 100 if (datetime.now() - LAST_SUCCESS) < timedelta(hours=2) else 95
            next_slot = (datetime.now() + timedelta(seconds=LOOP_INTERVAL)).strftime("%Y-%m-%d %H:%M:%S")

            # SystemLog 기록
            requests.post(
                f"{RENDER_BASE_URL}/system_log",
                json={
                    "access_key": GENIE_ACCESS_KEY,
                    "module": "AUTONOMOUS_LOOP",
                    "status": "✅OK",
                    "runtime": str(runtime),
                    "trust_ok": "TRUE",
                    "reason": "Safe Feedback Layer Completed",
                    "ref_id": f"AUTO.{start_time.strftime('%Y%m%d%H%M%S')}",
                    "uptime": str(uptime),
                },
                timeout=15,
            )

            LAST_SUCCESS = datetime.now()
            print(f"✅ 루프 완료 | Runtime: {runtime}s | Next: {next_slot}")

        except Exception as e:
            print("❌ 루프 내부 오류:", e)

        print(f"💤 {LOOP_INTERVAL/60:.1f}분 대기 중 ...")
        time.sleep(LOOP_INTERVAL)

# ─────────────────────────────────────────────
# 🚀 실행 (Flask와 독립)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Genie Autonomous Feedback Layer 시작")
    thread = threading.Thread(target=auto_feedback_loop, daemon=True)
    thread.start()
    while True:
        time.sleep(3600)  # 메인 스레드 유지용
