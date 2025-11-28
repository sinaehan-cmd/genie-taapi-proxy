import json, base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from genie_server.config import GOOGLE_SERVICE_ACCOUNT, SHEET_ID


# =============================================================
# Google Sheets Service
# =============================================================
def get_sheets_service(write=False):
    """Google Sheets API 서비스 객체 생성"""
    if not GOOGLE_SERVICE_ACCOUNT:
        raise ValueError("❌ GOOGLE_SERVICE_ACCOUNT not set")

    try:
        creds_json = base64.b64decode(GOOGLE_SERVICE_ACCOUNT).decode()
    except Exception:
        creds_json = GOOGLE_SERVICE_ACCOUNT.replace("\\n", "\n")

    creds_dict = json.loads(creds_json)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    if not write:
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    credentials = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=scopes
    )
    return build("sheets", "v4", credentials=credentials, cache_discovery=False)


# =============================================================
# Write Row (실제 쓰기)
# =============================================================
def write_row(sheet_name, row_values):
    """
    지정된 sheet_name 뒤에 row_values 추가
    """
    service = get_sheets_service(write=True)

    body = {"values": [row_values]}

    try:
        result = service.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range=sheet_name,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()

        return result

    except Exception as e:
        print("write_row Error:", e)
        raise


# =============================================================
# Compatibility Wrapper
# =============================================================
def append_row(sheet_name, row_values):
    """
    예전 코드 호환용 → 내부적으로 write_row 호출
    """
    try:
        return write_row(sheet_name, row_values)
    except Exception as e:
        print("append_row Error:", e)
        raise
