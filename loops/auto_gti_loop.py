# loops/auto_gti_loop.py

import traceback
import datetime
from services.auto_gti_service import run_auto_gti_core


def run_auto_gti_loop():
    """
    Auto GTI Loop wrapper
    - app(11).py의 자동 GTI 심화 루프 복원
    """
    start = datetime.datetime.now()
    result = {
        "event": "auto_gti_loop",
        "start": str(start)
    }

    try:
        core_result = run_auto_gti_core()
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
