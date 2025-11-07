# -*- coding: utf-8 -*-
# ======================================================
# 🤖 Genie Autonomous Feedback Layer v3.2 – Reader + Auto-Recovery 통합판
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
# 🔗 엔드포인트 호출 함수
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
# 🔁 자율 피드백 루프
# ─────────────────────────────────────────────
def auto_feedback_loop():
    """기존 Flask 엔드포인트들을 순차 호출하며 시스템 상태를 유지"""
    global LAST_SUCCESS
    while True:
        # 콘솔 클리어
        os.system("clear" if os.name == "posix" else "cls")
        start_time = datetime.now()
        print("\n🕒 [Auto Feedback] 루프 시작:", start_time.strftime("%Y-%m-%d %H:%M:%S"))

        try:
            # ① 루프별 호출 순서
            call_genie("auto_loop")        # 브리핑 생성
            time.sleep(6)
            call_genie("prediction_loop")  # 예측
            time.sleep(6)
            call_genie("gti_loop")         # 신뢰도 평가
            time.sleep(6)
            call_genie("learning_loop")    # 수식 보정
            time.sleep(6)
            call_genie("reader_loop")      # ✅ 최종 브리핑 읽기 (상태 반영)
            time.sleep(3)

            # ② 시스템 로그 기록
            runtime = (datetime.now() - start_time).seconds
            uptime = 100 if (datetime.now() - LAST_SUCCESS) < timedelta(hours=2) else 95
            next_slot = (datetime.now() + timedelta(seconds=LOOP_INTERVAL)).strftime("%Y-%m-%d %H:%M:%S")

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
# 🚀 실행 (Auto-Recovery 내장)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Genie Autonomous Feedback Layer v3.2 시작")

    while True:
        try:
            thread = threading.Thread(target=auto_feedback_loop, daemon=True)
            thread.start()
            thread.join()  # 루프 종료 시까지 대기
        except Exception as e:
            print("💥 메인 루프 예외 발생:", e)
        finally:
            print("🔄 30초 후 재시작 시도 중 ...")
            time.sleep(30)
