
import os
import json
import base64
from googleapiclient.discovery import build
from google.oauth2 import service_account

SHEET_ID = os.getenv("SHEET_ID")

# 서비스 계정 로드
def get_sheet_service():
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT")
    info = json.loads(base64.b64decode(raw))
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=creds).spreadsheets()

# 시트 읽기
def read_sheet(sheet_name):
    service = get_sheet_service()
    rng = f"{sheet_name}!A:Z"
    result = service.values().get(spreadsheetId=SHEET_ID, range=rng).execute()
    return result.get("values", [])

# append
def append_row(sheet_name, row):
    service = get_sheet_service()
    body = {"values": [row]}
    service.values().append(
        spreadsheetId=SHEET_ID,
        range=f"{sheet_name}!A:Z",
        valueInputOption="RAW",
        body=body
    ).execute()

# write to specific row-col
def write_row(sheet_name, row_index, values):
    service = get_sheet_service()
    rng = f"{sheet_name}!A{row_index}"
    body = {"values": [values]}
    service.values().update(
        spreadsheetId=SHEET_ID,
        range=rng,
        valueInputOption="RAW",
        body=body
    ).execute()
