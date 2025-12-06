# services/sheet_service.py
# unified sheet service — compatible with all Genie loops

import os
import json
import base64
from googleapiclient.discovery import build
from google.oauth2 import service_account

SHEET_ID = os.getenv("SHEET_ID")

# ============================================================
# FLOAT 변환
# ============================================================

def float_try(v):
    try:
        return float(v)
    except Exception:
        return None


# ============================================================
# Google Sheets 서비스 생성 (Lazy Singleton)
#  - 내부용: _get_raw_service()
#  - 외부용: get_sheet_service / get_sheets_service (둘 다 지원)
# ============================================================

_service_cache = None

def _get_raw_service():
    """실제 google sheets service.spreadsheets() 객체 생성"""
    global _service_cache
    if _service_cache is not None:
        return _service_cache

    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT")
    if not raw:
        raise Exception("❌ GOOGLE_SERVICE_ACCOUNT 환경변수 없음")

    info = json.loads(base64.b64decode(raw))

    creds = service_account.Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    service = build("sheets", "v4", credentials=creds)
    _service_cache = service.spreadsheets()
    return _service_cache


# 🔹 옛 코드 호환: 둘 다 같은 걸 리턴하도록 alias 제공

def get_sheet_service():
    """신규 표준 이름"""
    return _get_raw_service()

def get_sheets_service():
    """옛 이름 호환용"""
    return _get_raw_service()


# ============================================================
# READ RANGE
# ============================================================

def read_sheet(sheet_name: str):
    """
    예: read_sheet("genie_data_v5")
    → [["헤더1", ...], ["값1", ...], ...]
    """
    service = _get_raw_service()
    rng = f"{sheet_name}!A:Z"
    res = service.values().get(
        spreadsheetId=SHEET_ID,
        range=rng
    ).execute()
    return res.get("values", [])


def read_range(range_str: str):
    """
    예: read_range("genie_briefing_log!A:K")
    → {"range": ..., "values": [...]}
    """
    service = _get_raw_service()
    res = service.values().get(
        spreadsheetId=SHEET_ID,
        range=range_str
    ).execute()
    return res


# ============================================================
# APPEND (행 추가)
# ============================================================

def append_row(sheet_name_or_range: str, row: list):
    """
    예:
      append_row("genie_predictions", [...])
      append_row("genie_predictions!A:N", [...])
    """
    service = _get_raw_service()

    if "!A" not in sheet_name_or_range:
        rng = f"{sheet_name_or_range}!A:Z"
    else:
        rng = sheet_name_or_range

    body = {"values": [row]}

    return service.values().append(
        spreadsheetId=SHEET_ID,
        range=rng,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()


def append(range_str: str, values: list):
    """
    예:
      rows = [[...], [...]]
      append("genie_gti_log!A:J", rows)
    """
    service = _get_raw_service()
    body = {"values": values}

    return service.values().append(
        spreadsheetId=SHEET_ID,
        range=range_str,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()


# ============================================================
# WRITE (특정 row overwrite)
# ============================================================

def write_row(sheet_name: str, row_index: int, values: list):
    """
    예: write_row("genie_data_v5", 10, [...])
    """
    service = _get_raw_service()
    rng = f"{sheet_name}!A{row_index}"
    body = {"values": [values]}

    return service.values().update(
        spreadsheetId=SHEET_ID,
        range=rng,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()


def write(range_str: str, values: list):
    """
    예: write("genie_data_v5!A2:Z2", [[...]])
    """
    service = _get_raw_service()
    body = {"values": values}

    return service.values().update(
        spreadsheetId=SHEET_ID,
        range=range_str,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
