import requests, os
from genie_server.config import GENIE_ACCESS_KEY, RENDER_BASE_URL

ACCESS = GENIE_ACCESS_KEY
BASE = RENDER_BASE_URL

def send_to_sheet(sheet, values):
    """구글시트에 쓰기 위한 표준 함수"""
    payload = {
        "access_key": ACCESS,
        "sheet_name": sheet,
        "values": values
    }
    try:
        r = requests.post(f"{BASE}/write", json=payload, timeout=10)
        return r.status_code, r.text
    except Exception as e:
        return 500, str(e)
