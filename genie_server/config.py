import os

# 환경 변수 로드
TAAPI_KEY = os.getenv("TAAPI_KEY", "your_taapi_key_here")
SHEET_ID = os.getenv("SHEET_ID")
GOOGLE_SERVICE_ACCOUNT = os.getenv("GOOGLE_SERVICE_ACCOUNT")
GENIE_ACCESS_KEY = os.getenv("GENIE_ACCESS_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = "https://api.taapi.io"

def log_env_info():
    print("🔍 환경변수 로드 =======================")
    print("GOOGLE_SERVICE_ACCOUNT:", bool(GOOGLE_SERVICE_ACCOUNT))
    print("SHEET_ID:", SHEET_ID)
    print("GENIE_ACCESS_KEY:", bool(GENIE_ACCESS_KEY))
    print("OPENAI_API_KEY:", bool(OPENAI_API_KEY))
    print("TAAPI_KEY:", bool(TAAPI_KEY))
    print("==================================================")
