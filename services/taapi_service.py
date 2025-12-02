import requests
import os

# Render Proxy URL
PROXY_BASE = "https://genie-taapi-proxy-1.onrender.com"


def fetch_indicator(indicator, symbol="BTC/USDT", interval="1h", period=None):
    """
    모든 지표를 Proxy 서버에서 받아오는 공통 함수

    /indicator?indicator=rsi&symbol=BTC/USDT&interval=1h&period=14
    """
    try:
        url = f"{PROXY_BASE}/indicator?indicator={indicator}&symbol={symbol}&interval={interval}"

        if period:
            url += f"&period={period}"

        r = requests.get(url, timeout=10).json()
        return r.get("value")

    except Exception as e:
        print(f"❌ fetch_indicator error: {e}")
        return None


# ------------------------------
# 개별 helper 함수 (편의용)
# ------------------------------

def taapi_rsi(symbol="BTC/USDT", interval="1h", period=14):
    return fetch_indicator("rsi", symbol, interval, period)


def taapi_ema(symbol="BTC/USDT", interval="1h", period=20):
    return fetch_indicator("ema", symbol, interval, period)


def taapi_macd(symbol="BTC/USDT", interval="1h"):
    return fetch_indicator("macd", symbol, interval)
