import statistics
from services.google_sheet import read_last_rows


def parse_float(value):
    """문자열 또는 None을 안전하게 float로 변환"""
    try:
        return float(value)
    except:
        return None


def get_recent_dominance_values(hours):
    """
    최근 N시간의 dominance 값을 genie_data_v5 에서 읽어온다.
    hours = 4 → 4개의 1h 데이터
    hours = 24 → 24개의 1h 데이터
    """
    rows = read_last_rows("genie_data_v5", hours)

    values = []
    for row in rows:
        dom = parse_float(row.get("Dominance(%)"))
        if dom is not None:
            values.append(dom)

    return values


def get_dominance_avg(hours):
    """
    Dominance(4h), Dominance(1d)를 계산하는 메인 함수
    최근 N개의 데이터를 평균낸다.
    """
    values = get_recent_dominance_values(hours)

    if len(values) == 0:
        return None

    # 평균 계산
    avg_value = statistics.mean(values)

    # 지니 계산식 기준: 소수점 6자리 유지
    return round(avg_value, 6)
