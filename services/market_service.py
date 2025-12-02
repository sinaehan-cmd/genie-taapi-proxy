import requests

# -----------------------------
# USD/KRW 환율
# -----------------------------
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


# -----------------------------
# Fear & Greed Index
# -----------------------------
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


# -----------------------------
# BTC Dominance Snapshot
# -----------------------------
def dominance_snapshot():
    """
    BTC 도미넌스 스냅샷 (간단 버전)
    - /dominance/snapshot, /dominance/packet 둘 다 여기 기반으로 사용
    """
    try:
        url = "https://api.coingecko.com/api/v3/global"
        r = requests.get(url, timeout=5).json()
        data = r.get("data", {})

        dominance = data.get("market_cap_percentage", {}).get("btc")
        total_market_cap = data.get("total_market_cap", {}).get("usd")

        return {
            "btc_dominance": dominance,
            "total_market_cap_usd": total_market_cap,
        }
    except Exception as e:
        print("❌ Dominance fetch error:", e)
        return {
            "btc_dominance": None,
            "total_market_cap_usd": None,
        }

# -----------------------------
# MVRV Z-Score Fetcher (Basic)
# -----------------------------
def mvrv_run():
    """
    Coinglass or CryptoQuant API가 없기 때문에
    일단은 구조만 반환하는 더미 함수.
    나중에 실제 API 연결하면 여기에 붙이면 됨.
    """
    try:
        # 임시 값 (None 대신 기본값 0.0 반환)
        return {
            "btc_mvrv": 0.0,
            "eth_mvrv": 0.0,
            "note": "MVRV placeholder — API not connected yet"
        }
    except Exception as e:
        print("❌ MVRV fetch error:", e)
        return {
            "btc_mvrv": None,
            "eth_mvrv": None
        }

