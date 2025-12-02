import os
import requests

TAAPI_KEY = os.getenv("TAAPI_KEY")

BASE_URL = "https://api.taapi.io"

def fetch_indicator(indicator, symbol="BTC/USDT", interval="1h"):
    """
    TAAPI 요청 → Genie 서버가 직접 호출해서 반환하는 함수
    """
    try:
        url = f"{BASE_URL}/{indicator}"

        params = {
            "secret": TAAPI_KEY,
            "exchange": "binance",
            "symbol": symbol,
            "interval": interval
        }

        r = requests.get(url, params=params, timeout=8)
        data = r.json()

        # TAAPI가 에러 반환하면 바로 전달
        if "error" in data:
            return {"error": data["error"]}

        return data

    except Exception as e:
        return {"error": str(e)}
