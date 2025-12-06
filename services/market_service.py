import requests

# -----------------------------------------------------
# ✔ 공통 안전 요청 함수
# -----------------------------------------------------
def safe_request(url, timeout=5):
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ Request error: {url}", e)
        return None


# -----------------------------------------------------
# ✔ USD/KRW 환율
# -----------------------------------------------------
def get_usd_krw():
    """
    Dunamu 환율 API로 현재 USD/KRW 환율 가져오기
    """
    url = "https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD"
    data = safe_request(url)

    if not data or not isinstance(data, list):
        return None

    return data[0].get("basePrice")


# -----------------------------------------------------
# ✔ Fear & Greed Index
# -----------------------------------------------------
def get_fng_index():
    """
    Fear & Greed Index 가져오기
    """
    url = "https://api.alternative.me/fng/?limit=1"
    data = safe_request(url)

    if not data:
        return None

    value = data.get("data", [{}])[0].get("value")

    try:
        return int(value)
    except:
        return value
