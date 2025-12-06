# services/learning_service.py
# Genie Learning Loop — v9.3 정식 호환 버전

from datetime import datetime
from services.sheet_service import read_range, append, float_try


def safe_float(v):
    try:
        return float(v)
    except:
        return None


def run_learning_core():
    """
    Genie Learning Loop
    - 실제 데이터(genie_data_v5)
    - 예측 데이터(genie_predictions)
    - GTI 데이터(genie_gti_log)
    → 결합하여 genie_learning_log 에 저장
    """

    try:
        # ---------------------------------------------------
        # 1) 실제 데이터 불러오기 (genie_data_v5)
        # ---------------------------------------------------
        data = read_range("genie_data_v5!A:Z").get("values", [])
        if len(data) < 2:
            return {"error": "no genie_data_v5 data"}

        dh = data[0]
        last = data[-1]

        def ext_d(name):
            return last[dh.index(name)] if name in dh else None

        actual_price = safe_float(ext_d("BTC/USD"))
        actual_rsi = safe_float(ext_d("RSI(1h)"))
        dominance = safe_float(ext_d("Dominance(%)"))
        mvrv_z = safe_float(ext_d("MVRV_Z"))

        # ---------------------------------------------------
        # 2) 예측 데이터 (genie_predictions)
        # ---------------------------------------------------
        preds = read_range("genie_predictions!A:N").get("values", [])
        if len(preds) < 2:
            return {"error": "no prediction data"}

        ph = preds[0]
        last_p = preds[-1]

        def ext_p(name):
            return last_p[ph.index(name)] if name in ph else None

        pred_price = safe_float(ext_p("Predicted_Price"))
        pred_rsi = safe_float(ext_p("Predicted_RSI"))
        pred_dom = safe_float(ext_p("Predicted_Dominance"))

        # ---------------------------------------------------
        # 3) GTI 최신 데이터
        # ---------------------------------------------------
        gti = read_range("genie_gti_log!A:J").get("values", [])
        if len(gti) < 2:
            gti_score = None
        else:
            gh = gti[0]
            last_g = gti[-1]
            try:
                gti_score = float(last_g[gh.index("GTI_Score")])
            except:
                gti_score = None

        # ---------------------------------------------------
        # 4) 학습용 데이터 구성
        # ---------------------------------------------------
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [[
            now,
            actual_price,
            actual_rsi,
            dominance,
            mvrv_z,
            pred_price,
            pred_rsi,
            pred_dom,
            gti_score,
            "Auto-Learning"
        ]]

        # 헤더가 없으면 자동 생성
        check = read_range("genie_learning_log!A:J").get("values", [])
        if not check:
            append("genie_learning_log!A:J", [[
                "Timestamp", "Actual_Price", "Actual_RSI", "Dominance",
                "MVRV_Z", "Pred_Price", "Pred_RSI", "Pred_Dominance",
                "GTI_Score", "Note"
            ]])

        # ---------------------------------------------------
        # 5) 기록
        # ---------------------------------------------------
        append("genie_learning_log!A:J", row)

        return {
            "status": "logged",
            "row": row
        }

    except Exception as e:
        print("❌ learning_service error:", e)
        return {"error": str(e)}
