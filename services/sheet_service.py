# services/sheet_service.py
# Genie Loop Compatible Version (100% 루프 호환 복구판)

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
# Google Sheet Wrapper (루프 호환 클래스)
# ============================================================
class GenieSheet:
    def __init__(self, sheet_id, service):
        self.sheet_id = sheet_id
        self.service = service

    # ---- read_range ----
    def read_range(self, range_str):
        res = self.service.values().get(
            spreadsheetId=self.sheet_id,
            range=range_str
        ).execute()
        return res

    # ---- append ----
    def append(self, range_str, values):
        body = {"values": values}
        return self.service.values().append(
            spreadsheetId=self.sheet_id,
            range=range_str,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

    # ---- append_row ----
    def append_row(self, sheet_name_or_range, row):
        if "!A" not in sheet_name_or_range:
            rng = f"{sheet_name_or_range}!A:Z"
        else:
            rng = sheet_name_or_range

        body = {"values": [row]}
        return self.service.values().append(
            spreadsheetId=self.sheet_id,
            range=rng,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

    # ---- write ----
    def write(self, range_str, values):
        body = {"values": values}
        return self.service.values().update(
            spreadsheetId=self.sheet_id,
            range=range_str,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

    # ---- write_row ----
    def write_row(self, sheet_name, row_index, values):
        rng = f"{sheet_name}!A{row_index}"
        body = {"values": [values]}

        return self.service.values().update(
            spreadsheetId=self.sheet_id,
            range=rng,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()


# ============================================================
# Lazy Singleton
# ============================================================
_service_cache = None


def get_sheets_service():
    """
    Google Sheets API + GenieSheet wrapper 반환 (루프 100% 호환).
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

    api = build("sheets", "v4", credentials=creds).spreadsheets()
    wrapper = GenieSheet(SHEET_ID, api)

    _service_cache = wrapper
    return wrapper
