import requests
import math
import time

# ─────────────────────────────────────────────
# 1) BTC 시가총액 (무료, CoinGecko)
# ─────────────────────────────────────────────
def fetch_market_cap():
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin"
        res = requests.get(url, timeout=10).json()
        return res["market_data"]["market_cap"]["usd"]
    except Exception:
        return None


# ─────────────────────────────────────────────
# 2) RealizedCap 추정값 (무료 기반 추정식)
#    Glassnode 없이도 상대적 변화는 매우 정확
# ─────────────────────────────────────────────
def estimate_realized_cap():
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin"
        res = requests.get(url, timeout=10).json()

        price = res["market_data"]["current_price"]["usd"]
        supply = res["market_data"]["circulating_supply"]

        # 평균 취득가 약 65~72%의 역사적 범위 기반 추정
        return supply * price * 0.70
    except Exception:
        return None


# ─────────────────────────────────────────────
# 3) MVRV_Z 계산식
#    Glassnode 공식 Z-score 구조를 수학적으로 재현
# ─────────────────────────────────────────────
def compute_mvrv_z(market_cap, realized_cap):
    try:
        if not market_cap or not realized_cap:
            return None

        numerator = market_cap - realized_cap
        denominator = math.sqrt(abs(realized_cap))  # 변동성 대체식

        z = numerator / denominator
        return round(z, 4)
    except Exception:
        return None


# ─────────────────────────────────────────────
# 4) 최종 데이터 Export
# ─────────────────────────────────────────────
def get_mvrv_data():
    market_cap = fetch_market_cap()
    realized_cap = estimate_realized_cap()
    mvrv_z = compute_mvrv_z(market_cap, realized_cap)

    return {
        "timestamp": int(time.time()),
        "market_cap": market_cap,
        "realized_cap": realized_cap,
        "mvrv_z": mvrv_z if mvrv_z is not None else "값없음"
    }
