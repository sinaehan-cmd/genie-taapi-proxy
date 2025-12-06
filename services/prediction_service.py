# services/prediction_service.py
# app(11).py의 prediction_loop 로직 100% 복원 서비스 버전

from datetime import datetime, timedelta
from services.sheet_service import get_sheet_service, float_try   # ← 여기 수정


def run_prediction_core():
    """
    Prediction 코어 로직
    - genie_briefing_log 최신 데이터 기반 예측 생성
    - genie_predictions 시트에 한 줄 기록
    """
    try:
        service = get_sheet_service()   # ← 여기 수정
        sheet_id = service.sheet_id

        # -----------------------------------
        # 1) genie_briefing_log 최신 행 읽기
        # -----------------------------------
        src_range = "genie_briefing_log!A:K"
        result = service.read_range(src_range)
        values = result.get("values", [])

        if len(values) < 2:
            return {"error": "No briefing data"}

        headers = values[0]
        last = values[-1]

        def val(col):
            return last[headers.index(col)] if col in headers else ""

        btc_price = float_try(val("BTC_Price"))
        btc_rsi = float_try(val("BTC_RSI"))
        dominance = float_try(val("Dominance"))
        ref_id = val("Briefing_ID")

        # -----------------------------------
        # 2) 예측 시간 설정
        # -----------------------------------
        prediction_time = datetime.now()
        target_time = prediction_time + timedelta(hours=1)

        # -----------------------------------
        # 3) 예측 계산식 (기존 app(11).py의 정확한 방식)
        # -----------------------------------
        predicted_price = round(btc_price * (1 + (btc_rsi - 50) / 1000), 2)
        predicted_rsi = round(btc_rsi * 0.98 + 1, 2)
        predicted_dom = round(dominance + (btc_rsi - 50) / 200, 2)

        confidence = max(0, min(100, 100 - abs(50 - btc_rsi)))

        # -----------------------------------
        # 4) Prediction ID 생성
        # -----------------------------------
        prediction_id = f"P01.1.{prediction_time.strftime('%Y-%m-%d-%H:%M')}"

        # -----------------------------------
        # 5) 시트에 기록
        # -----------------------------------
        row_data = [[
            prediction_id,
            prediction_time.strftime("%Y-%m-%d %H:%M:%S"),
            target_time.strftime("%Y-%m-%d %H:%M:%S"),
            "BTC_USDT",
            predicted_price,
            predicted_rsi,
            predicted_dom,
            "LinearDelta(v1.1)",
            "AUTO",
            confidence,
            "",      # Actual Price (empty)
            "",      # Deviation (empty)
            ref_id,  # Reference briefing ID
            "Auto-predicted by Genie"
        ]]

        service.append("genie_predictions!A:N", row_data)

        return {
            "result": "logged",
            "Prediction_ID": prediction_id,
            "price": predicted_price,
            "rsi": predicted_rsi,
            "dominance": predicted_dom,
            "confidence": confidence
        }

    except Exception as e:
        print("❌ prediction_service error:", e)
        return {"error": str(e)}
