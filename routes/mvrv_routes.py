# services/mvrv_service.py
# -----------------------------------------------------
# Genie Internal MVRV-Z Calculator
# 실현가·표준편차 고정하여 안정적인 근사 MVRV-Z 생성
# -----------------------------------------------------

import math

# 지니가 자동 선택한 기준값
BTC_SUPPLY = 19_700_000             # 유통량 (대략 고정)
REALIZED_PRICE = 30_000             # ✅ 지니가 자동 결정한 실현가
STD = 1_000_000_000_000             # 표준편차 고정 (1조)

def calculate_mvrv_z(price):
    """
    MVRV-Z 근사 계산
    price: BTC 현재 가격(float)
    """
    try:
        if price is None:
            return None

        # MarketCap
        market_cap = price * BTC_SUPPLY

        # Realized Cap (고정값)
        realized_cap = REALIZED_PRICE * BTC_SUPPLY

        # Z-score
        z = (market_cap - realized_cap) / STD

        # 값 포맷
        return round(z, 4)

    except Exception:
        return None
