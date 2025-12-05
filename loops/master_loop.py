# loops/master_loop.py
# Genie Master Loop – 전체 루프 실행 엔진 (정확 복원 + 효율화 구조)

import datetime
import traceback

from loops.reader_loop import run_reader_loop
from loops.auto_briefing_loop import run_auto_briefing_loop
from loops.prediction_loop import run_prediction_loop
from loops.gti_loop import run_gti_loop
from loops.learning_loop import run_learning_loop
from loops.auto_gti_loop import run_auto_gti_loop
from loops.system_log_loop import run_system_log_loop


def run_master_loop():
    """
    Genie 전체 루프를 1회 실행.
    모든 개별 기능 루프를 순차 실행하고 결과를 dict로 반환한다.
    """
    start_time = datetime.datetime.now()

    result = {
        "start": str(start_time),
        "steps": [],
        "errors": []
    }

    # Safety wrapper for each step
    def step(name, fn):
        try:
            res = fn()
            result["steps"].append({name: res})
        except Exception as e:
            result["errors"].append(f"{name} Error: {str(e)}")
            result["errors"].append(traceback.format_exc())

    # 1) Reader (데이터 최신화)
    step("reader", run_reader_loop)

    # 2) Auto Briefing (genie_data_v5 → genie_briefing_log)
    step("auto_briefing", run_auto_briefing_loop)

    # 3) Prediction
    step("prediction", run_prediction_loop)

    # 4) GTI
    step("gti", run_gti_loop)

    # 5) Learning (계산식 저장)
    step("learning", run_learning_loop)

    # 6) Auto GTI (개선형 보조 루프)
    step("auto_gti", run_auto_gti_loop)

    # 7) System Log 기록
    step("system_log", run_system_log_loop)

    # 종료 정보
    end_time = datetime.datetime.now()
    result["end"] = str(end_time)
    result["duration_sec"] = (end_time - start_time).total_seconds()

    return result
