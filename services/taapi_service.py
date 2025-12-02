import requests

TAAPI = "https://api.taapi.io"
PROXY_BASE = "https://genie-taapi-proxy-1.onrender.com"

def fetch_indicator(indicator, symbol="BTC/USDT", interval="1h", period=None):
    """
    Proxy 서버에서 단일 value 지표 받아오기 (RSI, EMA 등)
    MACD는 여기서 호출하면 안 되고 별도 함수 사용해야 함.
    """
    try:
        # MACD는 별도 함수 사용하도록 보호
        if indicator.lower() == "macd":
            return None  

        url = f"{PROXY_BASE}/indicator?indicator={indicator}&symbol={symbol}&interval={interval}"
        if period:
            url += f"&period={period}"

        r = requests.get(url, timeout=8).json()
        return r.get("value")

    except Exception as e:
        print(f"❌ fetch_indicator error: {e}")
        return None


# ―――――――――――――――――――――――
# ⭐ MACD 전용 파서 (핵심)
# ―――――――――――――――――――――――
def taapi_macd(symbol="BTC/USDT", interval="1h"):
    """
    MACD는 valueMACD / valueMACDSignal / valueMACDHist 구조라
    Proxy 서버를 그대로 호출하면 안 되고 Raw 호출해야 한다.
    """
    try:
        url = f"{PROXY_BASE}/indicator?indicator=macd&symbol={symbol}&interval={interval}"
        r = requests.get(url, timeout=8).json()

        return {
            "macd": r.get("valueMACD"),
            "signal": r.get("valueMACDSignal"),
            "hist": r.get("valueMACDHist")
        }

    except Exception as e:
        print("❌ MACD fetch error:", e)
        return {"macd": None, "signal": None, "hist": None}


# ― 단일 지표 헬퍼 ―
def taapi_rsi(symbol="BTC/USDT", interval="1h", period=14):
    return fetch_indicator("rsi", symbol, interval, period)

def taapi_ema(symbol="BTC/USDT", interval="1h", period=20):
    return fetch_indicator("ema", symbol, interval, period)
