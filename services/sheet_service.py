import os
import json
import base64
from googleapiclient.discovery import build
from google.oauth2 import service_account

SHEET_ID = os.getenv("SHEET_ID")

# ------------------------------------------------------------
# 안전한 float 변환
# ------------------------------------------------------------
def float_try(v):
    try:
        return float(v)
    except:
        return None


# ------------------------------------------------------------
# 기존 네 구조: get_sheet_service() 유지
# ------------------------------------------------------------
_service_cache = None

def get_sheet_service():
    """
    기존 프로젝트 전체에서 사용하던 함수
    - get_sheet_service 그대로 유지
    - 내부 구조만 최신화
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

    # ✔ 네가 쓰던 패턴과 동일하게 attrs 추가
    _service_cache.sheet_id = SHEET_ID
    _service_cache.values = _service_cache.values()

    return _service_cache


# ------------------------------------------------------------
# READ
# ------------------------------------------------------------
def read_sheet(sheet_name):
    service = get_sheet_service()
    rng = f"{sheet_name}!A:Z"

    res = service.values.get(
        spreadsheetId=SHEET_ID, range=rng
    ).execute()

    return res.get("values", [])


def read_range(range_str):
    service = get_sheet_service()

    res = service.values.get(
        spreadsheetId=SHEET_ID, range=range_str
    ).execute()

    return res


# ------------------------------------------------------------
# APPEND
# ------------------------------------------------------------
def append_row(sheet_name_or_range, row):
    service = get_sheet_service()

    if "!A" not in sheet_name_or_range:
        rng = f"{sheet_name_or_range}!A:Z"
    else:
        rng = sheet_name_or_range

    body = {"values": [row]}

    return service.values.append(
        spreadsheetId=SHEET_ID,
        range=rng,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()


def append(range_str, values):
    service = get_sheet_service()
    body = {"values": values}

    return service.values.append(
        spreadsheetId=SHEET_ID,
        range=range_str,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()


# ------------------------------------------------------------
# WRITE
# ------------------------------------------------------------
def write_row(sheet_name, row_index, values):
    service = get_sheet_service()
    rng = f"{sheet_name}!A{row_index}"

    body = {"values": [values]}

    return service.values.update(
        spreadsheetId=SHEET_ID,
        range=rng,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()


def write(range_str, values):
    service = get_sheet_service()
    body = {"values": values}

    return service.values.update(
        spreadsheetId=SHEET_ID,
        range=range_str,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
