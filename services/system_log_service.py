# services/system_log_service.py
# Genie System Log — v9.3 완전 호환 버전

import datetime
from services.sheet_service import append, read_range


def run_system_log_core(status="OK", message=""):
    """
    시스템 상태 기록
    - 루프 실행 후 상태를 genie_system_log 시트에 기록
    """

    # --------------------------
    # 1) Timestamp
    # --------------------------
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --------------------------
    # 2) 헤더 확인 & 자동 생성
    # --------------------------
    rows = read_range("genie_system_log!A:C").get("values", [])
    if not rows:
        # 헤더 생성
        append("genie_system_log!A:C", [[
            "Timestamp", "Worker_Status", "Message"
        ]])

    # --------------------------
    # 3) 기록 데이터 구성
    # --------------------------
    row = [[now, status, message]]

    append("genie_system_log!A:C", row)

    return {
        "status": "logged",
        "timestamp": now,
        "worker_status": status,
        "message": message
    }
