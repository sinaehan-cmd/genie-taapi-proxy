import requests

# ----------------------------------------
# ✔ 공통 요청 함수 (안정성 강화)
# ----------------------------------------
def safe_request(url, timeout=5):
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ Request error: {url}", e)
        return None


# ----------------------------------------
# USD/KRW 환율
# ----------------------------------------
def get_usd_krw():
    """
    현재 USD/KRW 환율 가져오기
    """
    url = "https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD"
    data = safe_request(url)

    if not data or not isinstance(data, list):
        return None

    return data[0].get("basePrice")


# ----------------------------------------
# Fear & Greed Index
# ----------------------------------------
def get_fng_index():
    """
    Fear & Greed Index 값 가져오기
    """
    url = "https://api.alternative.me/fng/?limit=1"
    data = safe_request(url)

    if not data:
        return None

    value = data.get("data", [{}])[0].get("value")

    # 문자열이므로 숫자 변환 시도
    try:
        return int(value)
    except:
        return value  # 원본 그대로 반환


# ----------------------------------------
# BTC Dominance Snapshot
# ----------------------------------------
def dominance_snapshot():
    """
    BTC 도미넌스 스냅샷(간단 버전)
    /dominance/snapshot 과 /dominance/packet에서 공통 사용
    """
    url = "https://api.coingecko.com/api/v3/global"
    data = safe_request(url)

    if not data:
        return {
            "btc_dominance": None,
            "total_market_cap_usd": None,
        }

    inner = data.get("data", {})

    return {
        "btc_dominance": inner.get("market_cap_percentage", {}).get("btc"),
        "total_market_cap_usd": inner.get("total_market_cap", {}).get("usd"),
    }


# ----------------------------------------
# MVRV Z-Score Fetcher (placeholder)
# ----------------------------------------
def mvrv_run():
    """
    실제 API를 붙이기 전까지 구조만 반환하는 플레이스홀더
    """
    try:
        return {
            "btc_mvrv": 0.0,
            "eth_mvrv": 0.0,
            "note": "MVRV placeholder — API not connected yet"
        }
    except Exception as e:
        print("❌ MVRV fetch error:", e)
        return {
            "btc_mvrv": None,
            "eth_mvrv": None,
            "note": "error"
        }
