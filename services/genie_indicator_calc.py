# genie_indicator_calc.py
# Dominance(4h), Dominance(1d), MVRV_Z 계산 모듈

import time
import statistics
from collections import deque

# 최근 dominance 값 기록 (서버 리부트 전까지 유지됨)
dominance_history = deque(maxlen=48)   # 48개면 2일치 (1h 간격)

# 최근 BTC 가격 기록 – MVRV proxy 계산용
price_history = deque(maxlen=200)      # 200일 이동평균을 흉내내기 위한 200포인트


def record_values(dominance, btc_price):
    """매 시간 dominance & price 저장"""
    if dominance is not None:
        dominance_history.append(dominance)

    if btc_price is not None:
        price_history.append(btc_price)


def get_dominance_4h():
    """최근 4개(4시간)의 평균"""
    if len(dominance_history) < 4:
        return None
    return sum(list(dominance_history)[-4:]) / 4


def get_dominance_1d():
    """최근 24개(24시간)의 평균"""
    if len(dominance_history) < 24:
        return None
    return sum(list(dominance_history)[-24:]) / 24


def calc_mvrv_z():
    """BTC 가격 기반 MVRV-Z Proxy 계산"""

    if len(price_history) < 30:
        return 0   # 데이터 부족 → 0으로 반환

    mean = statistics.mean(price_history)
    std = statistics.pstdev(price_history)

    if std == 0:
        return 0

    current = price_history[-1]
    z = (current - mean) / std

    return round(z, 2)
