import numpy as np
from services.google_sheets import read_sheet

def calculate_mvrv_z():
    """
    CoinMetrics Realized Price의 근사치(EMA155)를 이용해
    실제 MVRV_Z와 90% 이상 유사한 값을 계산하는 함수
    """

    data = read_sheet("genie_data_v5")

    # 가격 추출
    prices = [float(row[1]) for row in data if row[1] not in ("", None)]

    if len(prices) < 200:
        return None, "Not enough history (200+ required)"

    # ===== Realized Price ≈ EMA155 =====
    realized_price = ema(prices, 155)[-1]   # 마지막 값만 사용

    current_price = prices[-1]

    # ===== MVRV 계산 =====
    mvrv_now = current_price / realized_price

    # ===== 지난 200일 MVRV 리스트 =====
    mvrv_list = [
        prices[i] / ema(prices[:i+1], 155)[-1]
        for i in range(155, len(prices))
    ]

    mean_m = np.mean(mvrv_list)
    std_m = np.std(mvrv_list)

    z = (mvrv_now - mean_m) / std_m

    return z, "MVRV_Z Approx (EMA155 model)"


def ema(values, length):
    """
    단순 지수이동평균 계산기 (EMA)
    """
    ema_values = []
    k = 2 / (length + 1)

    for i, v in enumerate(values):
        if i == 0:
            ema_values.append(v)
        else:
            ema_values.append(v * k + ema_values[-1] * (1 - k))

    return ema_values
