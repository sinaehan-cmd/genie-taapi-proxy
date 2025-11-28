# -*- coding: utf-8 -*-
# ============================================================
#  Genie System – Google Sheets Writer (Final Stable Edition)
#  v2025.11 – multi-sheet mapping + write/readonly + safe load
# ============================================================

import json, base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from genie_server.config import GOOGLE_SERVICE_ACCOUNT

# ------------------------------------------------------------
# 📌 1) 네 운영본 시트 구조 매핑 (2025-11-06 공식 버전)
# ------------------------------------------------------------
SHEET_MAP = {
    "genie_data_v5":        "YOUR_SHEET_ID_1",
    "genie_briefing_log":   "YOUR_SHEET_ID_2",
    "genie_predictions":    "YOUR_SHEET_ID_3",
    "genie_gti_log":        "YOUR_SHEET_ID_4",
    "genie_formula_store":  "YOUR_SHEET_ID_5",
    "genie_system_log":     "YOUR_SHEET_ID_6",
    "genie_alert_log":      "YOUR_SHEET_ID_7",
}

# ------------------------------------------------------------
# 📌 Config에서 Service Account 로드
# ------------------------------------------------------------
def _load_service_account():
    if not GOOGLE_SERVICE_ACCOUNT:
        raise ValueError("❌ GOOGLE_SERVICE_ACCOUNT 환경변수 누락")

    # base64 또는 plain JSON 모두 지원
    try:
        creds_json = base64.b64decode(GOOGLE_SERVICE_ACCOUNT).decode()
    except Exception:
        creds_json = GOOGLE_SERVICE_ACCOUNT.replace("\\n", "\n")

    return json.loads(creds_json)


# ------------------------------------------------------------
# 📌 Google Sheets API 클라이언트 생성
# ------------------------------------------------------------
def get_sheets_service(write=False):
    creds_dict = _load_service_account()

    scopes = (
        ["https://www.googleapis.com/auth/spreadsheets"]
        if write else
        ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )

    credentials = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=scopes
    )

    return build("sheets", "v4", credentials=credentials, cache_discovery=False)


# ------------------------------------------------------------
# 📌 내부 공통 유틸 – 시트명 → 실제 spreadsheet_id 변환
# ------------------------------------------------------------
def _get_sheet_id(sheet_name):
    if sheet_name not in SHEET_MAP:
        raise ValueError(f"❌ Unknown sheet: {sheet_name}")
    return SHEET_MAP[sheet_name]


# ------------------------------------------------------------
# 📘 write_row — 모든 쓰기 로직의 메인 함수
# ------------------------------------------------------------
def write_row(sheet_name, row_values):
    """
    지정된 sheet_name에 1행을 append
    RAW 모드로 정확한 값 입력
    """

    try:
        spreadsheet_id = _get_sheet_id(sheet_name)
        service = get_sheets_service(write=True)
        sheet = service.spreadsheets()

        # A:Z 등 큰 범위로 append 가능
        range_name = f"{sheet_name}!A1"

        body = {"values": [row_values]}

        result = sheet.values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body,
        ).execute()

        return result

    except Exception as e:
        print(f"write_row Error ({sheet_name}):", str(e))
        raise


# ------------------------------------------------------------
# 📘 append_row — 호환용 Wrapper
# ------------------------------------------------------------
def append_row(sheet_name, row_values):
    """
    예전 코드와의 호환을 위한 wrapper
    내부적으로 write_row 호출
    """
    return write_row(sheet_name, row_values)
