# loops/learning_loop.py
# Learning Loop Wrapper — app(11).py 기반 복원

import traceback
import datetime
from services.learning_service import run_learning_core


def run_learning_loop():
    """
    Learning Loop 실행
    - app(11).py 기준 Learning 기능 복원
    - learning_service.run_learning_core()를 감싼 wrapper
    """
    start = datetime.datetime.now()
    result = {
        "event": "learning_loop",
        "start": str(start)
    }

    try:
        core_res = run_learning_core()
        result["core"] = core_res
        result["status"] = "success"

    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)
        result["trace"] = traceback.format_exc()

    end = datetime.datetime.now()
    result["end"] = str(end)
    result["duration_sec"] = (end - start).total_seconds()

    return result
