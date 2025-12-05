# loops/auto_loop.py
# app(11).py 기반 복원 버전

import traceback
import datetime

from loops.prediction_loop import run_prediction_loop
from loops.gti_loop import run_gti_loop
from loops.learning_loop import run_learning_loop
from loops.reader_loop import run_reader_loop
from loops.system_log_loop import run_system_log_loop
from loops.auto_gti_loop import run_auto_gti_loop


def run_auto_loop():
    """
    자동 루프 1회 실행 (app(11).py의 auto_loop 로직 복원)
    """
    start_time = datetime.datetime.now()

    result = {
        "start": str(start_time),
        "steps": [],
        "errors": []
    }

    try:
        # 1) Reader / Data Fetch
        try:
            reader_res = run_reader_loop()
            result["steps"].append({"reader": reader_res})
        except Exception as e:
            result["errors"].append(f"Reader Error: {str(e)}")

        # 2) Prediction
        try:
            pred_res = run_prediction_loop()
            result["steps"].append({"prediction": pred_res})
        except Exception as e:
            result["errors"].append(f"Prediction Error: {str(e)}")

        # 3) GTI Update
        try:
            gti_res = run_gti_loop()
            result["steps"].append({"gti": gti_res})
        except Exception as e:
            result["errors"].append(f"GTI Error: {str(e)}")

        # 4) Learning 저장
        try:
            learning_res = run_learning_loop()
            result["steps"].append({"learning": learning_res})
        except Exception as e:
            result["errors"].append(f"Learning Error: {str(e)}")

        # 5) Auto GTI (심화 루프)
        try:
            auto_gti_res = run_auto_gti_loop()
            result["steps"].append({"auto_gti": auto_gti_res})
        except Exception as e:
            result["errors"].append(f"Auto GTI Error: {str(e)}")

        # 6) System Log 기록
        try:
            syslog_res = run_system_log_loop()
            result["steps"].append({"system_log": syslog_res})
        except Exception as e:
            result["errors"].append(f"System Log Error: {str(e)}")

    except Exception as e:
        result["errors"].append(f"Auto Loop Fatal Error: {str(e)}")
        result["trace"] = traceback.format_exc()

    end_time = datetime.datetime.now()
    result["end"] = str(end_time)
    result["duration_sec"] = (end_time - start_time).total_seconds()

    return result
