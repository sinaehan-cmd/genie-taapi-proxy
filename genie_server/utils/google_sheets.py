# -*- coding: utf-8 -*-
"""
Genie Server — Google Sheets Utility (v2025.11 Stable)
완전 동작 / append_row + write_row + read_sheet 모두 포함
"""

import json, base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from genie_server.config import GOOGLE_SERVICE_ACCOUNT, SHEET_ID


# ------------------------------------------------------------
# 1) Google Sheets 서비스 객체 생성
# ------------------------------------------------------------
def get_sheets_service(write=False):
    if not GOOGLE_SERVICE_ACCOUNT:
        raise ValueError("❌ GOOGLE_SERVICE_ACCOUNT not set")

    # Base64 → JSON 디코딩
    try:
        creds_json = base64.b64decode(GOOGLE_SERVICE_ACCOUNT).decode()
    except Exception:
        # Render에서 \n 이스케이프된 버전 대응
        creds_json = GOOGLE_SERVICE_ACCOUNT.replace("\\n", "\n")

    creds_dict = json.loads(creds_json)

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    if not write:
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    credentials = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=scopes
    )

    return build("sheets", "v4", credentials=credentials, cache_discovery=False)


# ------------------------------------------------------------
# 2) write_row — 시트에 1행 추가 (append)
# ------------------------------------------------------------
def write_row(sheet_name, row_values):
    """
    공식 시트 쓰기 함수.
    append_row()는 이걸 감싸는 wrapper.
    """
    service = get_sheets_service(write=True)

    body = {
        "values": [row_values]
    }

    service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range=sheet_name,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()

    return True


# ------------------------------------------------------------
# 3) append_row — 호환성 wrapper
# ------------------------------------------------------------
def append_row(sheet_name, row_values):
    try:
        return write_row(sheet_name, row_values)
    except Exception as e:
        print("append_row Error:", e)
        raise


# ------------------------------------------------------------
# 4) read_sheet — 읽기 용도
# ------------------------------------------------------------
def read_sheet(sheet_name):
    service = get_sheets_service(write=False)
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=sheet_name
    ).execute()

    return result.get("values", [])
