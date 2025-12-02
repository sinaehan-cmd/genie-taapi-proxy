from services.google_sheets import read_sheet, append_row
from services.market_service import get_usd_krw, get_fng_index
from services.taapi_service import taapi_rsi   # ⭐ 반드시 추가
import datetime


def run_prediction_loop():
    data = read_sheet("genie_data_v5")

    if len(data) < 2:
        return "No data"

    last = data[-1]

    # -------------------------
    # genie_data_v5 컬럼 구조
    # 0: timestamp
    # 1: BTC
    # 2: ETH
    # 3: SOL
    # 4: XRP
    # 5: Dominance
    # 6: RSI(1h)
    # ...
    # -------------------------

    timestamp = datetime.datetime.now().isoformat()

    btc_price = last[1]              # OK
    dominance = last[5]              # ⭐ index 수정 (3 → 5)
    rsi_1h = taapi_rsi("BTC/USDT", "1h")
    fng = get_fng_index()
    usdkrw = get_usd_krw()

    # 간단 공식
    predicted = float(btc_price) * 1.01

    row = [
        timestamp,         # Prediction_Time
        timestamp,         # Target_Time
        "BTC",             # Symbol
        predicted,         # Predicted_Price
        rsi_1h,            # Predicted_RSI
        dominance,         # Predicted_Dominance
        "simple_formula",  # Formula
        "NEUTRAL",         # Interpretation_Code
        0.7,               # Confidence
        "",                # Actual_Price
        "",                # Deviation
        "",                # Reference_ID
        "",                # Comment
    ]

    append_row("genie_predictions", row)
    return "Prediction appended"
