# services/mvrv_service.py
import math
import requests
import logging

# -----------------------------
# 1) Price History Buffer
# -----------------------------
PRICE_HISTORY = []
MAX_HISTORY = 200  # 최소 200개 필요 (근사 정확도 ↑)


def update_price_history(price: float):
    """가격 히스토리 갱신"""
    if price is None:
        return

    PRICE_HISTORY.append(price)

    if len(PRICE_HISTORY) > MAX_HISTORY:
        PRICE_HISTORY.pop(0)


# -----------------------------
# 2) Realized Price Reconstruction
# -----------------------------
def calc_realized_price():
    """
    온체인 Realized Price 근사
    방식:
      - 가격 변동 시, 이전 가격을 weighted buying price 로 축적
      - 이동 평균 기반 매입단가 근사
    """
    if len(PRICE_HISTORY) < 30:
        return None  # 안정적 계산 불가

    # 단순 이동 평균 기반 근사
    window = PRICE_HISTORY[-60:] if len(PRICE_HISTORY) >= 60 else PRICE_HISTORY
    realized_price = sum(window) / len(window)

    return realized_price


# -----------------------------
# 3) MarketCap & RealizedCap
# -----------------------------
BTC_SUPPLY = 19_700_000  # 근사치. 원하면 최신 공급량 API도 붙일 수 있음.

def calc_market_cap(price):
    return price * BTC_SUPPLY


def calc_realized_cap(realized_price):
    return realized_price * BTC_SUPPLY


# -----------------------------
# 4) Z-score 구현
# -----------------------------
Z_HISTORY = []
Z_STD_WINDOW = 120  # 표준편차 계산용 윈도우


def calc_mvrv_z(price: float):
    """
    Glassnode MVRV-Z 공식 근사:

        Z = (MarketCap - RealizedCap) / std(MarketCap history)

    - std는 장기 윈도우 기반
    - Realized Price는 Reconstruction 방식
    """

    # 가격 기록
    update_price_history(price)

    if len(PRICE_HISTORY) < 60:
        return None

    realized_price = calc_realized_price()
    if realized_price is None:
        return None

    mc = calc_market_cap(price)
    rc = calc_realized_cap(realized_price)
    diff = mc - rc

    # Z-score 표준편차 기록
    Z_HISTORY.append(mc)
    if len(Z_HISTORY) > Z_STD_WINDOW:
        Z_HISTORY.pop(0)

    # 표준편차 계산
    if len(Z_HISTORY) < 30:
        return None

    mean_mc = sum(Z_HISTORY) / len(Z_HISTORY)
    variance = sum((x - mean_mc) ** 2 for x in Z_HISTORY) / len(Z_HISTORY)
    std_mc = math.sqrt(variance)

    if std_mc == 0:
        return None

    z = diff / std_mc
    return round(z, 4)
