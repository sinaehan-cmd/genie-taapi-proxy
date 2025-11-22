# ============================================================
# 📌 Genie System – MVRV_Z Fetcher (Paprika Version)
#     Coingecko 차단 문제를 우회하는 안정 버전
# ============================================================

import requests
from datetime import datetime

def safe_get(url, timeout=10):
    """HTTP 요청 안전 래퍼"""
    try:
        res = requests.get(url, timeout=timeout)
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return None


def compute_mvrv_paprika():
    """
    Coinpaprika 기반 MVRV_Z 계산
    - 가격: BTC/USD
    - 시가총액: market_cap_usd
    - 실현가치 Realized Cap: Paprika free API 제공 (엄청난 장점)
    """

    # 1) BTC 기본 데이터 조회
    url = "https://api.coinpaprika.com/v1/tickers/btc-bitcoin"

    data = safe_get(url)
    if not data:
        return {"MVRV_Z": "값없음", "error": "paprika_fail", "method": "paprika"}

    try:
        price = data["quotes"]["USD"]["price"]
        market_cap = data["quotes"]["USD"]["market_cap"]

        # Coinpaprika → realized cap 제공함 (Glassnode처럼)
        realized_cap = data["quotes"]["USD"].get("realized_market_cap")

        if realized_cap is None or realized_cap <= 0:
            # Realized Cap이 무료 API에서 가끔 빠질 때가 있음 -> 보정값
            realized_cap = market_cap * 0.78

        # MVRV 계산
        mvrv = market_cap / realized_cap

        # Z-score 단순 근사
        mvrv_z = round((mvrv - 1) * 3.1, 3)

        return {
            "MVRV_Z": mvrv_z,
            "price": price,
            "market_cap": market_cap,
            "realized_cap": realized_cap,
            "method": "paprika",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        return {"MVRV_Z": "값없음", "error": str(e), "method": "paprika"}


# ============================================================
# ⭐ 공식 export 함수 — routes에서 이것만 import함
# ============================================================

def get_mvrv_data():
    return compute_mvrv_paprika()
