import json, base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from genie_server.config import GOOGLE_SERVICE_ACCOUNT


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

