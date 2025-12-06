# loops/master_loop.py
# Genie Master Loop – 60분 반복 안정판 (Render Worker 전용)

import time
import datetime
import traceback

from loops.reader_loop import run_reader_loop
from loops.prediction_loop import run_prediction_loop
from loops.gti_loop import run_gti_loop
from loops.learning_loop import run_learning_loop
from loops.auto_gti_loop import run_auto_gti_loop
from loops.system_log_loop import run_system_log_loop

# auto_briefing_loop은 있을 수도, 없을 수도 있음 → Optional import
try:
    from loops.auto_briefing_loop import run_auto_briefing_loop
    HAS_BRIEFING = True
except Exception:
    HAS_BRIEFING = False
    def run_auto_briefing_loop():
        return {"status": "skipped", "reason": "auto_briefing_loop.py not found"}


INTERVAL_MINUTES = 60  # 60분 주기


def start_master_loop():
    """
    Render Worker에서 실행되는 루프
    - 절대 종료되지 않음
    - 60분마다 전체 자동 루프 1회 실행
    """
    print("🔄 Genie Master Loop initiated.")
    print(f"⏱ 실행 주기: {INTERVAL_MINUTES}분")

    while True:

        loop_start = datetime.datetime.now()
        print("\n" + "=" * 60)
        print(f"🚀 [Master Loop] 실행 시작: {loop_start}")

        result = {
            "start": str(loop_start),
            "steps": [],
            "errors": []
        }

        def step(name, fn):
            """각 step 실행 + 오류를 잡고 넘어감"""
            try:
                res = fn()
                result["steps"].append({name: res})
            except Exception as e:
                err = f"{name} Error: {str(e)}"
                result["errors"].append(err)
                result["errors"].append(traceback.format_exc())
                print(f"❌ {err}")

        # ------------------------------
        # ▶ 전체 루프 순서
        # ------------------------------

        step("reader", run_reader_loop)

        if HAS_BRIEFING:
            step("auto_briefing", run_auto_briefing_loop)
        else:
            result["steps"].append(
                {"auto_briefing": "skipped (module missing)"}
            )

        step("prediction", run_prediction_loop)
        step("gti", run_gti_loop)
        step("learning", run_learning_loop)
        step("auto_gti", run_auto_gti_loop)
        step("system_log", run_system_log_loop)

        # ------------------------------
        # ▶ 종료 처리
        # ------------------------------
        loop_end = datetime.datetime.now()
        runtime_sec = (loop_end - loop_start).total_seconds()

        print("📘 [Master Loop] 실행 결과:")
        print(result)

        print(f"⏳ 실행 시간: {runtime_sec:.1f}초")
        print(f"💤 다음 실행까지 대기: {INTERVAL_MINUTES}분")
        print("=" * 60)

        # 계속 반복 (절대 종료되지 않음)
        time.sleep(INTERVAL_MINUTES * 60)
