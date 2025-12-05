# loops/prediction_loop.py

import traceback
import datetime
from services.prediction_service import run_prediction_core


def run_prediction_loop():
    """
    Prediction 루프 실행
    - app(11).py 기준 prediction 엔드포인트 기능 복원
    """
    start = datetime.datetime.now()
    result = {
        "event": "prediction_loop",
        "start": str(start)
    }

    try:
        core_result = run_prediction_core()
        result["core"] = core_result
        result["status"] = "success"

    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)
        result["trace"] = traceback.format_exc()

    end = datetime.datetime.now()
    result["end"] = str(end)
    result["duration_sec"] = (end - start).total_seconds()

    return result
