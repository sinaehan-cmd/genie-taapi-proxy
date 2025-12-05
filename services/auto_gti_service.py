# services/auto_gti_service.py
# Auto GTI Core — app(11).py 기반 복원 버전

import statistics
from services.sheet_service import read_sheet, append_row
from services.gti_service import safe_float


def run_auto_gti_core():
    """
    Auto GTI 심화 루프
    - 예측/실제 비교 패턴 기반 보조 GTI 업데이트
    - 매 루프마다 최근 오차 5~20개 패턴을 분석
    """

    # 최신 30개 예측 데이터 가져오기
    preds = read_sheet("genie_predictions")[-30:]
    if not preds:
        return {"status": "no_data"}

    deviations = []

    for row in preds:
        dev = safe_float(row.get("Deviation(%)"))
        if dev is not None:
            deviations.append(dev)

    if not deviations:
        return {"status": "no_valid_deviation"}

    avg_dev = statistics.mean(deviations)
    max_dev = max(deviations)
    min_dev = min(deviations)

    # 보조 GTI 지표 계산 (예: deviation 기반 score)
    adjusted_score = max(0, 100 - avg_dev * 3)
    adjusted_score = min(adjusted_score, 100)

    record = {
        "AVG_Deviation": round(avg_dev, 3),
        "MIN_Deviation": round(min_dev, 3),
        "MAX_Deviation": round(max_dev, 3),
        "Adjusted_GTI": round(adjusted_score, 2)
    }

    append_row("genie_gti_log", record)

    return {
        "status": "success",
        "auto_gti_record": record
    }
