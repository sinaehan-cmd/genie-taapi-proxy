import requests
import os

TAAPI_KEY = os.getenv("TAAPI_KEY")
TAAPI_BASE = "https://api.taapi.io"


def _call_taapi(endpoint, params):
    """TAAPI를 직접 호출하는 안전한 공통 함수"""
    try:
        params["secret"] = TAAPI_KEY
        url = f"{TAAPI_BASE}/{endpoint}"
        r = requests.get(url, params=params, timeout=8).json()

        return r
    except Exception as e:
        print("❌ TAAPI error:", e)
        return None


# --------------------------------------------------------
# RSI (value 반환)
# --------------------------------------------------------
def taapi_rsi(symbol="BTC/USDT", interval="1h", period=14):
    r = _call_taapi("rsi", {
        "exchange": "binance",
        "symbol": symbol,
        "interval": interval,
        "optInTimePeriod": period
    })

    if not r:
        return {"value": None}

    return {"value": r.get("value")}


# --------------------------------------------------------
# EMA (value 반환)
# --------------------------------------------------------
def taapi_ema(symbol="BTC/USDT", interval="1h", period=20):
    r = _call_taapi("ema", {
        "exchange": "binance",
        "symbol": symbol,
        "interval": interval,
        "optInTimePeriod": period
    })

    if not r:
        return {"value": None}

    return {"value": r.get("value")}


# --------------------------------------------------------
# MACD (3종 반환)
# --------------------------------------------------------
def taapi_macd(symbol="BTC/USDT", interval="1h"):
    r = _call_taapi("macd", {
        "exchange": "binance",
        "symbol": symbol,
        "interval": interval
    })

    if not r:
        return {"macd": None, "signal": None, "hist": None}

    return {
        "macd": r.get("valueMACD"),
        "signal": r.get("valueMACDSignal"),
        "hist": r.get("valueMACDHist")
    }
