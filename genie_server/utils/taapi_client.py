# genie_server/utils/taapi_client.py
import requests
import os

TAAPI_KEY = os.getenv("TAAPI_KEY")
BASE_URL = "https://api.taapi.io"

def fetch_indicator(indicator="rsi", symbol="BTC/USDT", interval="1h", period=None):
    """Fetch a TAAPI indicator"""
    try:
        params = {
            "secret": TAAPI_KEY,
            "exchange": "binance",
            "symbol": symbol,
            "interval": interval
        }
        if period:
            params["period"] = period

        url = f"{BASE_URL}/{indicator}"
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        # Normal indicators
        if "value" in data:
            return data["value"]

        # MACD
        if "valueMACD" in data:
            return data["valueMACD"]

        # If TAAPI returns error format
        return None
    except Exception:
        return None
