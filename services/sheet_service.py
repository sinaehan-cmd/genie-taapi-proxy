# services/sheet_service.py
# Genie OS – Unified Google Sheets Service (Stable v2.0)

import os
import json
import base64
from googleapiclient.discovery import build
from google.oauth2 import service_account

# ------------------------------------------------------------
# 환경변수
# ------------------------------------------------------------
SHEET_ID = os.getenv("SHEET_ID")

# ------------------------------------------------------------
# 숫자 변환
# ------------------------------------------------------------
def float_try(v):
    try:
        return float(v)
    except:
        return None


# ------------------------------------------------------------
# Lazy Singleton Sheets client
# ------------------------------------------------------------
_service = None

def _build_service():
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT")
    if not raw:
        raise Exception("❌ GOOGLE_SERVICE_ACCOUNT 환경변수 없음")

    info = json.loads(base64.b64decode(raw))

    creds = service_account.Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    return build("sheets", "v4", credentials=creds).spreadsheets()


def get_sheets():
    global _service
    if _service is None:
        _service = _build_service()
    return _service


# ------------------------------------------------------------
# READ
# ------------------------------------------------------------

def read_sheet(sheet_name):
    """
    예: read_sheet("genie_data_v5")
    """
    service = get_sheets()
    rng = f"{sheet_name}!A:Z"

    res = service.values().get(
        spreadsheetId=SHEET_ID,
        range=rng
    ).execute()

    return res.get("values", [])


def read_range(range_str):
    """
    예: read_range("genie_predictions!A:N")
    """
    service = get_sheets()

    res = service.values().get(
        spreadsheetId=SHEET_ID,
        range=range_str
    ).execute()

    return res


# ------------------------------------------------------------
# APPEND
# ------------------------------------------------------------

def append_row(sheet_or_range, row):
    """
    예: append_row("genie_predictions", [...])
    """
    service = get_sheets()

    # sheetName → sheetName!A:Z 자동 변환
    if "!A" not in sheet_or_range:
        rng = f"{sheet_or_range}!A:Z"
    else:
        rng = sheet_or_range

    return service.values().append(
        spreadsheetId=SHEET_ID,
        range=rng,
        valueInputOption="USER_ENTERED",
        body={"values": [row]}
    ).execute()


def append(range_str, values):
    """
    예: append("genie_predictions!A:N", [[...], [...]])
    """
    service = get_sheets()

    return service.values().append(
        spreadsheetId=SHEET_ID,
        range=range_str,
        valueInputOption="USER_ENTERED",
        body={"values": values}
    ).execute()


# ------------------------------------------------------------
# WRITE
# ------------------------------------------------------------

def write_row(sheet_name, row_index, values):
    """
    예: write_row("genie_predictions", 10, [...])
    """
    service = get_sheets()
    rng = f"{sheet_name}!A{row_index}"

    return service.values().update(
        spreadsheetId=SHEET_ID,
        range=rng,
        valueInputOption="USER_ENTERED",
        body={"values": [values]}
    ).execute()


def write(range_str, values):
    """
    예: write("genie_predictions!D10", [[123]])
    """
    service = get_sheets()

    return service.values().update(
        spreadsheetId=SHEET_ID,
        range=range_str,
        valueInputOption="USER_ENTERED",
        body={"values": values}
    ).execute()
