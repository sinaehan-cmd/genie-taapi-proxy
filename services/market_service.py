import requests

def get_usd_krw():
    """
    USD/KRW 환율 조회
    (업비트 두나무 환율 API — 안정적)
    실패 시 '값없음' 반환
    """
    url = "https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD"

    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list) and len(data) > 0:
                return round(float(data[0].get("basePrice", "값없음")), 2)

        return "값없음"

    except Exception:
        return "값없음"



def get_fng_index():
    """
    Fear & Greed Index 조회
    실패 시 '값없음' 반환
    """
    url = "https://api.alternative.me/fng/?limit=1"

    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            value = data.get("data", [{}])[0].get("value")
            return value if value is not None else "값없음"

        return "값없음"

    except Exception:
        return "값없음"
