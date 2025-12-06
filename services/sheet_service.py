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
    except:
        return None


# ============================================================
# Google Sheets 서비스 생성 (Lazy Singleton)
# ============================================================

_service_cache = None


def get_sheets_service():
    """
    기존 네 구조(get_sheet_service) + Genie 전체 서비스 호환 버전.
    Singleton 형태로 객체 재사용.
    """
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


# ============================================================
# READ RANGE
# ============================================================

def read_sheet(sheet_name):
    """
    기존 네가 쓰던 read_sheet 그대로 유지.
    """
    service = get_sheets_service()
    rng = f"{sheet_name}!A:Z"
    res = service.values().get(
        spreadsheetId=SHEET_ID, range=rng
    ).execute()
    return res.get("values", [])


def read_range(range_str):
    """
    prediction_service / gti_service / learning_service 에 필요.
    """
    service = get_sheets_service()
    res = service.values().get(
        spreadsheetId=SHEET_ID, range=range_str
    ).execute()
    return res


# ============================================================
# APPEND (행 추가)
# ============================================================

def append_row(sheet_name_or_range, row):
    """
    기존 네 함수 + Genie 내부 append 형식도 지원.
    """
    service = get_sheets_service()

    # sheet_name!A:Z 또는 직접 range 둘 다 지원
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


def append(range_str, values):
    """
    prediction_service / gti_service 에 필요한 append wrapper
    """
    service = get_sheets_service()
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

def write_row(sheet_name, row_index, values):
    service = get_sheets_service()
    rng = f"{sheet_name}!A{row_index}"
    body = {"values": [values]}

    return service.values().update(
        spreadsheetId=SHEET_ID,
        range=rng,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()


def write(range_str, values):
    """
    Genie 내부 overwrite 방식.
    """
    service = get_sheets_service()
    body = {"values": values}

    return service.values().update(
        spreadsheetId=SHEET_ID,
        range=range_str,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
