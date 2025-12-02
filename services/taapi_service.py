import requests
import os

# Render BASE URL
RENDER_BASE = os.getenv("RENDER_BASE", "https://genie-taapi-proxy-1.onrender.com")


def taapi_rsi(symbol="BTC/USDT", interval="1h"):
    """
    Render 프록시를 통해 TAAPI RSI 가져오기
    """
    try:
        url = (
            f"{RENDER_BASE}/indicator"
            f"?indicator=rsi"
            f"&symbol={symbol}"
            f"&interval={interval}"
        )
        r = requests.get(url, timeout=5).json()
        return r.get("value")
    except Exception as e:
        print("❌ TAAPI RSI fetch error:", e)
        return None


def taapi_ema(symbol="BTC/USDT", interval="1h", period=20):
    """
    Render 프록시를 통해 TAAPI EMA 가져오기
    """
    try:
        url = (
            f"{RENDER_BASE}/indicator"
            f"?indicator=ema"
            f"&symbol={symbol}"
            f"&interval={interval}"
            f"&period={period}"
        )
        r = requests.get(url, timeout=5).json()
        return r.get("value")
    except Exception as e:
        print("❌ TAAPI EMA fetch error:", e)
        return None


def taapi_macd(symbol="BTC/USDT", interval="1h"):
    """
    Render 프록시를 통해 TAAPI MACD 가져오기
    """
    try:
        url = (
            f"{RENDER_BASE}/indicator"
            f"?indicator=macd"
            f"&symbol={symbol}"
            f"&interval={interval}"
        )
        r = requests.get(url, timeout=5).json()

        # TAAPI는 valueMACD / valueSignal / valueHistogram 구조일 수 있음
        return r.get("valueMACD") or r.get("value")
    except Exception as e:
        print("❌ TAAPI MACD fetch error:", e)
        return None
