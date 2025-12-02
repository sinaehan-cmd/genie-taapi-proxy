import requests
import math
import statistics

# 이동평균 기간
WINDOW = 180

# 지니 고유 스무딩 계수
LAMBDA = 0.94


def fetch_btc_history(days=WINDOW):
    """
    BTC 과거 가격을 CoinGecko에서 가져옴.
    """
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}"
    r = requests.get(url, timeout=10).json()

    prices = [p[1] for p in r.get("prices", [])]
    return prices[-WINDOW:] if len(prices) >= WINDOW else prices


def calculate_realized_cap(prices):
    """
    지니 근사 Realized Cap 계산:
    - 과거 가격의 지수 가중 평균 기반
    """
    if not prices:
        return None

    weights = [(LAMBDA ** i) for i in range(len(prices))]
    weights.reverse()

    realized = sum(p * w for p, w in zip(prices, weights)) / sum(weights)
    return realized


def calculate_std(prices):
    """
    시장 변동성 근사 (Glassnode 방식의 rolling variance simple 버전)
    """
    if not prices or len(prices) < 30:
        return None

    return statistics.pstdev(prices)


def calc_mvrv_z(current_price=None):
    """
    ⭐ 지니 오리지널 MVRV_Z 계산 공식 복원본
    """

    try:
        prices = fetch_btc_history()

        if not prices:
            return None

        # 실시간 가격 없으면 최근 값 사용
        if current_price is None:
            current_price = prices[-1]

        realized_cap = calculate_realized_cap(prices)
        std = calculate_std(prices)

        if realized_cap is None or std is None or std == 0:
            return None

        # Glassnode MVRV_Z 근사 공식
        mvrv_z = (current_price - realized_cap) / std

        return round(mvrv_z, 4)

    except Exception as e:
        print("MVRV calculation error:", e)
        return None
