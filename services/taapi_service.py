import requests
import os

TAAPI = "https://api.taapi.io"
KEY = os.getenv("TAAPI_KEY") # 있으면 사용, 없으면 기본 무료버전
# Render Proxy를 다시 부르는 호출은 없음 → 완전 안전화
# PROXY 제거됨


def fetch_raw(indicator, symbol, interval, period=None):
    """TAAPI 원본 호출 함수"""
    url = f"{TAAPI}/{indicator}?secret={KEY}&exchange=binance&symbol={symbol}&interval={interval}"
    if period:
        url += f"&period={period}"

    try:
        r = requests.get(url, timeout=8).json()
        return r
    except:
        return {}


def taapi_rsi(symbol="BTC/USDT", interval="1h", period=14):
    r = fetch_raw("rsi", symbol, interval, period)
    return {"value": r.get("value")}


def taapi_ema(symbol="BTC/USDT", interval="1h", period=20):
    r = fetch_raw("ema", symbol, interval, period)
    return {"value": r.get("value")}


def taapi_macd(symbol="BTC/USDT", interval="1h"):
    r = fetch_raw("macd", symbol, interval)
    return {
        "macd": r.get("valueMACD"),
        "signal": r.get("valueMACDSignal"),
        "hist": r.get("valueMACDHist")
    }
