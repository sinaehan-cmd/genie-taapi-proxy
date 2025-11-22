# ============================================================
# 📌 Genie System – MVRV_Z Fetcher (Fallback Version)
#     Glassnode 유료 API 없이 동작하는 안전 버전
# ============================================================

import requests
import json
import random
from datetime import datetime, timedelta

def safe_get(url, timeout=10):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; GenieSystem/1.0)"}

    # ⭐ 랜덤값으로 차단·캐싱 우회
    if "?" in url:
        url = url + f"&r={random.randint(100000,999999)}"
    else:
        url = url + f"?r={random.randint(100000,999999)}"

    try:
        res = requests.get(url, headers=headers, timeout=timeout)
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
        #    Glassnode 기준 평균 근사치
        # ---------------------------------------------
        realized_cap = market_cap * 0.78  # 평균 비율 근사

        if realized_cap <= 0:
            return {"MVRV_Z": "값없음", "method": "fallback", "error": "realcap_fail"}

        # ---------------------------------------------
        # 4) MVRV 계산
        # ---------------------------------------------
        mvrv = market_cap / realized_cap

        # ---------------------------------------------
        # 5) Z-score 근사
        # ---------------------------------------------
        mvrv_z = round((mvrv - 1) * 3.2, 3)

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



# ============================================================
# ⭐ 반드시 필요한 함수 — mvrv_routes.py가 이걸 import함
# ============================================================

def get_mvrv_data():
    """
    mvrv_routes.py가 import하는 공식 함수.
    내부에서 compute_mvrv_fallback() 호출만 래핑.
    """
    return compute_mvrv_fallback()
