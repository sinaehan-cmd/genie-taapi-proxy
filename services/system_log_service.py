# services/system_log_service.py
# System Log Core — app(11).py 기반 복원

import datetime
from services.sheet_service import append_row


def run_system_log_core(status="OK", message=None):
    """
    시스템 상태 기록
    - 자동 루프가 끝날 때마다 실행
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    record = {
        "Timestamp": now,
        "Worker_Status": status,
        "Message": message or "",
    }

    append_row("genie_system_log", record)

    return {
        "status": "success",
        "recorded": record
    }
