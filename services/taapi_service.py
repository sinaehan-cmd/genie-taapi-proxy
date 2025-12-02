
import os
import requests

TAAPI_KEY = os.getenv("TAAPI_KEY")

def taapi_rsi(symbol="BTC/USDT", interval="1h"):
    url = f"https://api.taapi.io/rsi?secret={TAAPI_KEY}&exchange=binance&symbol={symbol}&interval={interval}"
    res = requests.get(url).json()
    return res.get("value")
