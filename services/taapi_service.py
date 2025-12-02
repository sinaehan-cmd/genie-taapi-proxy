import requests
import os

# 실제 TAAPI API URL
TAAPI_BASE = "https://api.taapi.io"

# 환경변수에서 KEY 읽기
TAAPI_KEY = os.getenv("TAAPI_KEY")


def fetch_indicator(indicator, symbol="BTC/USDT", interval="1h", period=None):
    """
    Proxy가 아닌, 실제 TAAPI.io API를 직접 호출하는 함수
    """

    try:
        params = {
            "secret": TAAPI_KEY,
            "exchange": "binance",
            "symbol": symbol,
            "interval": interval
        }

        if period:
            params["period"] = period

        url = f"{TAAPI_BASE}/{indicator}"
        r = requests.get(url, params=params, timeout=10).json()

        return r.get("value")

    except Exception as e:
        print(f"❌ fetch_indicator error: {e}")
        return None


# 개별 helper
def taapi_rsi(symbol="BTC/USDT", interval="1h", period=14):
    return fetch_indicator("rsi", symbol, interval, period)


def taapi_ema(symbol="BTC/USDT", interval="1h", period=20):
    return fetch_indicator("ema", symbol, interval, period)


def taapi_macd(symbol="BTC/USDT", interval="1h"):
    return fetch_indicator("macd", symbol, interval)
