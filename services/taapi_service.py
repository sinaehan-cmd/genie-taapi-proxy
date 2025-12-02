# services/taapi_service.py
import os
import requests

TAAPI_KEY = os.getenv("TAAPI_KEY")

def fetch_indicator(indicator, symbol, interval, period=None):
    try:
        url = f"https://api.taapi.io/{indicator}"
        params = {
            "secret": TAAPI_KEY,
            "exchange": "binance",
            "symbol": symbol,
            "interval": interval
        }
        if period:
            params["period"] = period

        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
        return {"value": "값없음"}

    except Exception as e:
        return {"value": "값없음"}
