import requests
import math

SHEET_JSON_URL = "https://genie-taapi-proxy-1.onrender.com/view-json/genie_data_v5"


def get_recent_prices(limit=48):
    """최근 BTC 가격 48개 가져오기 (1h * 48)"""
    try:
        r = requests.get(SHEET_JSON_URL, timeout=5).json()

        prices = []
        for row in r.get("data", []):
            p = row.get("BTC/USD")
            if p:
                prices.append(p)

        return prices[-limit:]

    except:
        return []


def calc_mvrv_z():
    """Genie 근사식 MVRV_Z 계산"""

    prices = get_recent_prices()
    if len(prices) < 30:
        return None

    current_price = prices[-1]

    # 네트워크 평균 매입가 근사치
    realized_price = sum(prices[-30:]) / 30

    # 단순 표준편차 근사치
    deviation = math.sqrt(
        sum((p - realized_price) ** 2 for p in prices[-30:]) / 30
    )
    if deviation == 0:
        deviation = 1  # 안전장치

    z = (current_price - realized_price) / deviation
    return round(z, 3)
