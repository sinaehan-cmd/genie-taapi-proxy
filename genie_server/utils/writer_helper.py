import requests, os
from genie_server.config import GENIE_ACCESS_KEY, RENDER_BASE_URL

ACCESS = GENIE_ACCESS_KEY
BASE = RENDER_BASE_URL

def send_to_sheet(sheet, values):
    """루프에서 직접 구글시트 쓰고 싶을 때 사용"""
    payload = {
        "access_key": ACCESS,
        "sheet_name": sheet,
        "values": values
    }
    try:
        r = requests.post(f"{BASE}/write", json=payload, timeout=12)
        return r.status_code, r.text
    except Exception as e:
        return 500, str(e)
