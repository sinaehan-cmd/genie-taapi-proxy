# -*- coding: utf-8 -*-
# ======================================================
# 🤖 Genie Autonomous Feedback Layer v4.0
#   — New Module Structure Compatible Version
# ======================================================

import time, requests, os, threading
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# ⚙️ 환경 변수
# ─────────────────────────────────────────────
GENIE_ACCESS_KEY = os.getenv("GENIE_ACCESS_KEY")
RENDER_BASE_URL = os.getenv("RENDER_BASE_URL", "https://genie-taapi-proxy-1.onrender.com")
LOOP_INTERVAL = int(os.getenv("GENIE_LOOP_INTERVAL", 3600))  # 기본 1시간

LAST_SUCCESS = datetime.now()


# ─────────────────────────────────────────────
# 🔗 엔드포인트 안전 POST 호출
# ─────────────────────────────────────────────
def call_genie(endpoint: str):
    url = f"{RENDER_BASE_URL}/{endpoint}"
    try:
        res = requests.post(url, json={"access_key": GENIE_ACCESS_KEY}, timeout=20)

        if res.status_code == 200:
            print(f"✅ {endpoint} OK:", res.text[:120])
        else:
            print(f"⚠️ {endpoint} 실패 → {res.status_code}: {res.text}")

    except Exception as e:
        print(f"❌ {endpoint} 호출 오류:", e)


# ─────────────────────────────────────────────
# 🔁 메인 피드백 루프
# ─────────────────────────────────────────────
def auto_feedback_loop():
    global LAST_SUCCESS

    while True:
        start_time = datetime.now()
        start_label = start_time.strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n🕒 [Auto Feedback Loop] 시작: {start_label}")

        try:
            # ------------------------------------------------------
            # 1) Market Auto Loop
            # ------------------------------------------------------
            call_genie("loop/auto")
            time.sleep(2)

            # ------------------------------------------------------
            # 2) Prediction Loop
            # ------------------------------------------------------
            call_genie("loop/prediction")
            time.sleep(2)

            # ------------------------------------------------------
            # 3) GTI Loop
            # ------------------------------------------------------
            call_genie("loop/gti")
            time.sleep(2)

            # ------------------------------------------------------
            # 4) Learning Loop
            # ------------------------------------------------------
            call_genie("loop/learning")
            time.sleep(2)

            # ------------------------------------------------------
            # 5) Auto GTI Loop
            # ------------------------------------------------------
            call_genie("loop/auto_gti")
            time.sleep(2)

            # ------------------------------------------------------
            # 6) Dominance Snapshot
            # ------------------------------------------------------
            call_genie("dominance/snapshot")
            time.sleep(2)

            # ------------------------------------------------------
            # 7) MVRV Loop
            # ------------------------------------------------------
            call_genie("mvrv/run")
            time.sleep(2)

            # ------------------------------------------------------
            # 8) Reader Loop
            # ------------------------------------------------------
            call_genie("reader/run")
            time.sleep(2)

            # ------------------------------------------------------
            # 9) 시스템 로그 기록
            # ------------------------------------------------------
            runtime = (datetime.now() - start_time).seconds
            uptime = 100 if (datetime.now() - LAST_SUCCESS) < timedelta(hours=2) else 95

            call_genie("system/log")

            LAST_SUCCESS = datetime.now()

            print(f"✅ 루프 완료 | Runtime: {runtime}s")

        except Exception as e:
            print("❌ 루프 내부 오류:", e)

        # ------------------------------------------------------
        # 다음 루프까지 대기
        # ------------------------------------------------------
        next_time = datetime.now() + timedelta(seconds=LOOP_INTERVAL)
        print(f"💤 대기: {LOOP_INTERVAL/60:.1f}분 | Next: {next_time.strftime('%H:%M:%S')}\n")

        time.sleep(LOOP_INTERVAL)


# ─────────────────────────────────────────────
# 🚀 start_master_loop — Flask와 함께 실행되는 백그라운드 루프
# ─────────────────────────────────────────────
def start_master_loop():
    """Flask 서버와 동시에 자동 루프를 백그라운드에서 실행"""
    try:
        t = threading.Thread(target=auto_feedback_loop, daemon=True)
        t.start()
        print("🚀 start_master_loop() — Genie Auto Feedback Loop Started")
    except Exception as e:
        print("❌ start_master_loop 오류:", e)


# ─────────────────────────────────────────────
# Standalone 실행 (개발 모드)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Genie Autonomous Feedback v4.0 실행 시작")
    auto_feedback_loop()
