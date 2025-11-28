# -*- coding: utf-8 -*-
# ==========================================================
# 📄 Genie Sheet Writer v3.0 (Render Safe Version)
# 공통 Google Sheets 쓰기 모듈
# ==========================================================

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

GOOGLE_SERVICE_ACCOUNT = os.getenv("GOOGLE_SERVICE_ACCOUNT")
SHEET_ID = os.getenv("SHEET_ID")

service = None

# ----------------------------------------------------------
# 1) Google 인증 초기화
# ----------------------------------------------------------
def init_service():
    global service

    if service:
        return service

    try:
        info = json.loads(GOOGLE_SERVICE_ACCOUNT)
        creds = service_account.Credentials.from_service_account_info(
            info,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        service = build("sheets", "v4", credentials=creds, cache_discovery=False)
        print("🟢 Google Sheets Service initialized")
        return service

    except Exception as e:
        print("❌ Google Sheets Init Error:", e)
        service = None
        return None


# ----------------------------------------------------------
# 2) 공통 Write 함수
# ----------------------------------------------------------
def write_to_sheet(sheet_name: str, values: list):
    """
    특정 시트(sheet_name)의 마지막 줄에 values를 append 한다.
    """
    try:
        svc = init_service()
        if svc is None:
            print("❌ write_to_sheet 실패: Sheets 서비스 없음")
            return False, "SERVICE_INIT_FAIL"

        body = {"values": [values]}

        svc.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range=f"{sheet_name}!A1",
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()

        print(f"📝 기록 성공 → {sheet_name} | {values[:3]} ...")
        return True, "OK"

    except Exception as e:
        print(f"❌ write_to_sheet Error [{sheet_name}]:", e)
        return False, str(e)
