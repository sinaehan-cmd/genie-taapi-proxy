from services.google_sheets import read_sheet, append_row
from services.market_service import get_usd_krw, get_fng_index
import datetime

def run_prediction_loop():
    data = read_sheet("genie_data_v5")

    if len(data) < 2:
        return "No data"

    last = data[-1]
    
    timestamp = datetime.datetime.now().isoformat()
    btc_price = last[1]
    dominance = last[3]

    # ⭐ TAAPI 직접 호출 제거
    rsi_1h = last[5] if len(last) > 5 else None
    
    fng = get_fng_index()
    usdkrw = get_usd_krw()

    predicted = float(btc_price) * 1.01  # 샘플 공식

    row = [
        timestamp,
        timestamp,
        "BTC",
        predicted,
        rsi_1h,
        dominance,
        "simple_formula",
        "NEUTRAL",
        0.7,
        "",
        "",
        "",
        "",
    ]
    append_row("genie_predictions", row)
    return "Prediction appended"
