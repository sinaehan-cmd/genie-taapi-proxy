# loops/master_loop.py
# Genie Master Loop – 전체 루프 실행 엔진 (v2025.12 안정판)

import datetime
import traceback
import time

from loops.reader_loop import run_reader_loop
from loops.auto_briefing_loop import run_auto_briefing_loop
from loops.prediction_loop import run_prediction_loop
from loops.gti_loop import run_gti_loop
from loops.learning_loop import run_learning_loop
from loops.auto_gti_loop import run_auto_gti_loop
from loops.system_log_loop import run_system_log_loop


# -------------------------------------------------------
# 1) 1회 실행 로직 — 핵심 엔진
# -------------------------------------------------------
def run_master_once():
    """
    Genie 전체 루프를 1회 실행하고 결과 dict를 반환한다.
    """
    start_time = datetime.datetime.now()
    result = {
        "start": str(start_time),
        "steps": [],
        "errors": []
    }

    def step(name, fn):
        try:
            res = fn()
            result["steps"].append({name: res})
        except Exception as e:
            result["errors"].append(f"{name} Error: {str(e)}")
            result["errors"].append(traceback.format_exc())

    # 실행 순서
    step("reader", run_reader_loop)
    step("auto_briefing", run_auto_briefing_loop)
    step("prediction", run_prediction_loop)
    step("gti", run_gti_loop)
    step("learning", run_learning_loop)
    step("auto_gti", run_auto_gti_loop)
    step("system_log", run_system_log_loop)

    end_time = datetime.datetime.now()
    result["end"] = str(end_time)
    result["duration_sec"] = (end_time - start_time).total_seconds()

    return result


# -------------------------------------------------------
# 2) Worker 모드용 무한 루프
# -------------------------------------------------------
def start_master_loop():
    """
    Worker 모드에서 계속 실행되는 자동 루프.
    기본 인터벌: 3600초(1시간) – 필요 시 조절 가능.
    """
    INTERVAL_SEC = 3600   # 1시간 간격

    print("🟢 Genie Master Loop (worker) STARTED")

    while True:
        try:
            run_master_once()
        except Exception as e:
            print("❌ Master loop fatal error:", e)

        time.sleep(INTERVAL_SEC)
