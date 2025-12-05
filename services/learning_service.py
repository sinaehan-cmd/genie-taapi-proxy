# services/learning_service.py
# app(11).py 기반 리포팅/학습용 데이터 누적 로직 완전 복원

from datetime import datetime
from services.sheet_service import get_sheets_service


def safe_float(x):
    try:
        return float(x)
    except:
        return None


def run_learning_core():
    """
    Learning Loop Core
    - 최신 데이터들을 결합하여 genie_learning_log 에 누적 기록
    - 향후 예측 모델 개선용 데이터셋 역할
    """
    try:
        service = get_sheets_service()

        # ----------------------------------------
        # 1) 실제 데이터 (가격, RSI 등)
        # ----------------------------------------
        data_res = service.read_range("genie_data_v5!A:Z").get("values", [])
        if len(data_res) < 2:
            return {"error": "no genie_data_v5 data"}
        dh = data_res[0]
        last_data = data_res[-1]

        # ----------------------------------------
        # 2) 예측 데이터 (가장 최근 1개)
        # ----------------------------------------
        pred_res = service.read_range("genie_predictions!A:N").get("values", [])
        if len(pred_res) < 2:
            return {"error": "no prediction data"}
        ph = pred_res[0]
        last_pred = pred_res[-1]

        # ----------------------------------------
        # 3) GTI 최신값
        # ----------------------------------------
        gti_res = service.read_range("genie_gti_log!A:J").get("values", [])
        if len(gti_res) < 2:
            gti_score = None
        else:
            gh = gti_res[0]
            last_gti = gti_res[-1]
            try:
                gti_score = float(last_gti[gh.index("GTI_Score")])
            except:
                gti_score = None

        # ----------------------------------------
        # 4) 필요한 주요 컬럼만 추출
        # ----------------------------------------
        def extract(header, row, name):
            return row[header.index(name)] if name in header else None

        record_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 실제값
        actual_price = safe_float(extract(dh, last_data, "BTC/USD"))
        actual_rsi = safe_float(extract(dh, last_data, "RSI"))
        dominance = safe_float(extract(dh, last_data, "Dominance"))
        mvrv_z = safe_float(extract(dh, last_data, "MVRV_Z"))

        # 예측값
        pred_price = safe_float(extract(ph, last_pred, "Predicted_Price"))
        pred_rsi = safe_float(extract(ph, last_pred, "Predicted_RSI"))
        pred_dominance = safe_float(extract(ph, last_pred, "Predicted_Dominance"))

        # ----------------------------------------
        # 5) 학습용 row 구성
        # ----------------------------------------
        row = [[
            record_time,
            actual_price,
            actual_rsi,
            dominance,
            mvrv_z,
            pred_price,
            pred_rsi,
            pred_dominance,
            gti_score,
            "Auto-Learning"
        ]]

        # ----------------------------------------
        # 6) 시트 기록
        # ----------------------------------------
        service.append("genie_learning_log!A:J", row)

        return {
            "status": "logged",
            "row": row,
            "message": "learning row appended"
        }

    except Exception as e:
        return {"error": str(e)}
