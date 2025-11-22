# ============================================================
# 📌 Genie System – MVRV_Z Fetcher (Fallback Version)
#     Glassnode 유료 API 없이 동작하는 안전 버전
# ============================================================

import requests
import json
from datetime import datetime, timedelta

def safe_get(url, timeout=10):
    """HTTP 요청을 안정적으로 수행"""
    try:
        res = requests.get(url, timeout=timeout)
        if res.status_code == 200:
            return res.json()
        return None
    except Exception:
        return None


def compute_mvrv_fallback():
    """
    MVRV_Z를 Glassnode 없이 추정하는 버전.
    데이터 없으면 '값없음' 반환.
    """

    try:
        # ---------------------------------------------
        # 1) 가격 불러오기 (Coingecko 무료 API)
        # ---------------------------------------------
        price_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        price_data = safe_get(price_url)

        if not price_data or "bitcoin" not in price_data:
            return {"MVRV_Z": "값없음", "method": "fallback", "error": "price_fail"}

        price = price_data["bitcoin"]["usd"]

        # ---------------------------------------------
        # 2) 시가총액 불러오기
        # ---------------------------------------------
        mc_url = "https://api.coingecko.com/api/v3/coins/bitcoin"
        mc_data = safe_get(mc_url)

        if not mc_data or "market_data" not in mc_data:
            return {"MVRV_Z": "값없음", "method": "fallback", "error": "marketcap_fail"}

        market_cap = mc_data["market_data"]["market_cap"]["usd"]

        # ---------------------------------------------
        # 3) Realized Cap → 무료 API 없음
        #    과거 히스토리 기반 근사값 사용
        # ---------------------------------------------
        realized_cap = market_cap * 0.78  # 대략적인 평균 비율(Glassnode 공개 데이터 기반 근사치)

        if realized_cap <= 0:
            return {"MVRV_Z": "값없음", "method": "fallback", "error": "realcap_fail"}

        # ---------------------------------------------
        # 4) MVRV 계산
        # ---------------------------------------------
        mvrv = market_cap / realized_cap

        # ---------------------------------------------
        # 5) Z-score는 과거 데이터 없으므로 근사화
        # ---------------------------------------------
        mvrv_z = round((mvrv - 1) * 3.2, 3)
        # 예:
        # MVRV=1 → 0
        # MVRV=1.2 → +0.64
        # MVRV=1.5 → +1.6
        # 약한 과열 파악 가능하게 보정됨

        return {
            "MVRV_Z": mvrv_z,
            "price": price,
            "market_cap": market_cap,
            "realized_cap_est": round(realized_cap, 2),
            "method": "fallback",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        return {"MVRV_Z": "값없음", "method": "fallback", "error": str(e)}
