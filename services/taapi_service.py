import requests

BASE_URL = "https://genie-taapi-proxy-1.onrender.com"

# ------------------------------------------------
# Render TAAPI Proxy Wrapper
# ------------------------------------------------
def fetch_indicator(indicator, symbol="BTC/USDT", interval="1h", **kwargs):
    """
    /indicator API를 호출하는 공용 함수
    Apps Script · prediction_loop · 전략실 모두 여기 사용
    """
    try:
        params = {
            "indicator": indicator,
            "symbol": symbol,
            "interval": interval,
        }
        params.update(kwargs)

        url = f"{BASE_URL}/indicator"
        r = requests.get(url, params=params, timeout=5).json()
        return r

    except Exception as e:
        print("❌ fetch_indicator error:", e)
        return {"value": None}


# ------------------------------------------------
# 헬퍼 함수들
# ------------------------------------------------

def taapi_rsi(symbol="BTC/USDT", interval="1h"):
    r = fetch_indicator("rsi", symbol, interval)
    return r.get("value")


def taapi_ema(symbol="BTC/USDT", interval="1h", period=20):
    r = fetch_indicator("ema", symbol, interval, period=period)
    return r.get("value")


def taapi_macd(symbol="BTC/USDT", interval="1h"):
    r = fetch_indicator("macd", symbol, interval)
    return r.get("valueMACD") or r.get("value")
