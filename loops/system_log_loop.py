# loops/system_log_loop.py

import traceback
import datetime
from services.system_log_service import run_system_log_core


def run_system_log_loop():
    """
    System Log Loop wrapper
    - 자동 루프 마지막 단계 (상태 기록)
    """
    start = datetime.datetime.now()
    result = {
        "event": "system_log_loop",
        "start": str(start)
    }

    try:
        core_res = run_system_log_core()
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
