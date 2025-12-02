# services/mvrv_service.py
from services.google_sheets import read_sheet
import numpy as np

def calculate_mvrv_z():
    """
    Genie의 가격 데이터(genie_data_v5)를 기반으로
    BTC MVRV Z-Score를 추정해 반환한다.
    """

    try:
        data = read_sheet("genie_data_v5")

        if len(data) < 160:
            return None, "not enough data (>=160 rows needed)"

        # -------------------------
        # 1) 가장 최근 BTC 가격
        # -------------------------
        last = data[-1]
        btc_price = float(last[1])   # 2번째 컬럼이 BTC/USD

        # -------------------------
        # 2) long-term average (155-step EMA)
        # -------------------------
        prices = [float(row[1]) for row in data[-200:]]

        ema_155 = ema(prices, 155)

        # -------------------------
        # 3) standard deviation
        # -------------------------
        std = np.std(prices)

        # -------------------------
        # 4) Z-score 계산
        # -------------------------
        if std == 0:
            return None, "std=0 error"

        z = (btc_price - ema_155) / std

        return round(z, 3), "EMA155 model"

    except Exception as e:
        return None, f"error: {str(e)}"


# ------------------------------------------------------
# 내부 보조 함수: EMA (지수 이동 평균)
# ------------------------------------------------------

def ema(values, period):
    alpha = 2 / (period + 1)
    ema_val = values[0]

    for price in values[1:]:
        ema_val = alpha * price + (1 - alpha) * ema_val

    return ema_val
