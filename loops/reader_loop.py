# loops/reader_loop.py

import traceback
import datetime
from services.reader_service import run_reader_core


def run_reader_loop():
    """
    Reader Loop wrapper
    - app(11).py 데이터 수집 단계 복원
    """
    start = datetime.datetime.now()
    result = {
        "event": "reader_loop",
        "start": str(start)
    }

    try:
        core_res = run_reader_core()
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
