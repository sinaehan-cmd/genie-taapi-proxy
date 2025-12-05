# loops/gti_loop.py

import traceback
import datetime
from services.gti_service import run_gti_core


def run_gti_loop():
    """
    GTI 루프 실행
    - app(11).py 기준 GTI 갱신 기능 복원
    """
    start = datetime.datetime.now()
    result = {
        "event": "gti_loop",
        "start": str(start)
    }

    try:
        core_res = run_gti_core()
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
