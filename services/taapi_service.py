import requests
import os

# 실제 TAAPI.io URL
TAAPI_BASE = "https://api.taapi.io"

# Render Proxy BASE는 여기서 절대 호출하지 않는다!!
# PROXY_BASE = "https://genie-taapi-proxy-1.onrender.com"

TAAPI_KEY = os.getenv("TAAPI_KEY")


# ---------------------------------------------------------
# 🔥 공통: TAAPI.io 직접 호출 (절대 Proxy 호출 없음)
# ---------------------------------------------------------
def get_taapi_indicator(indicator, symbol="BTC/USDT", interval="1h", period=None):
    """
    /indicator 내부에서 다시 /indicator 호출하는 무한루프 제거 버전.
    이제 모든 지표는 TAAPI.io 원본 API에서 직접 가져온다.
    """
    try:
        url = f"{TAAPI_BASE}/{indicator}"

        params = {
            "secret": TAAPI_KEY,
            "exchange": "binance",
            "symbol": symbol,
            "interval": interval
        }

        if period:
            params["period"] = period

        r = requests.get(url, params=params, timeout=8)

        if r.status_code != 200:
            return "값없음"

        data = r.json()

        # 공통 value 반환
        value = data.get("value")
        return {"value": value} if value is not None else {"value": "값없음"}

    except Exception as e:
        print("❌ TAAPI indicator error:", e)
        return {"value": "값없음"}


# ---------------------------------------------------------
# 🔥 MACD 전용
# ---------------------------------------------------------
def taapi_macd(symbol="BTC/USDT", interval="1h"):
    """
    MACD는 valueMACD, valueMACDSignal, valueMACDHist 구조.
    이 역시 TAAPI.io 원본에서 직접 가져온다.
    """
    try:
        url = f"{TAAPI_BASE}/macd"

        params = {
            "secret": TAAPI_KEY,
            "exchange": "binance",
            "symbol": symbol,
            "interval": interval
        }

        r = requests.get(url, params=params, timeout=8)

        if r.status_code != 200:
            return {"macd": None, "signal": None, "hist": None}

        data = r.json()

        return {
            "macd": data.get("valueMACD"),
            "signal": data.get("valueMACDSignal"),
            "hist": data.get("valueMACDHist")
        }

    except Exception as e:
        print("❌ MACD fetch error:", e)
        return {"macd": None, "signal": None, "hist": None}


# ---------------------------------------------------------
# 단일 헬퍼
# ---------------------------------------------------------
def taapi_rsi(symbol="BTC/USDT", interval="1h", period=14):
    return get_taapi_indicator("rsi", symbol, interval, period)


def taapi_ema(symbol="BTC/USDT", interval="1h", period=20):
    return get_taapi_indicator("ema", symbol, interval, period)
