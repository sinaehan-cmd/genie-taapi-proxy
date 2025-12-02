import requests

def get_usd_krw():
    """
    현재 USD/KRW 환율 가져오기
    """
    try:
        url = "https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD"
        r = requests.get(url, timeout=5).json()
        return r[0].get("basePrice")
    except Exception as e:
        print("❌ USD/KRW fetch error:", e)
        return None


def get_fng_index():
    """
    Fear & Greed Index 가져오기
    """
    try:
        url = "https://api.alternative.me/fng/?limit=1"
        r = requests.get(url, timeout=5).json()
        return r["data"][0].get("value")
    except Exception as e:
        print("❌ FNG fetch error:", e)
        return None
