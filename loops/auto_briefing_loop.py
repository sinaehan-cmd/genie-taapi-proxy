# loops/auto_briefing_loop.py
# Genie Auto-Briefing Loop (2025.12 Stable)
# app(11).py의 핵심 브리핑 생성 기능 100% 복원

from datetime import datetime
import random
from services.sheet_service import (
    read_range,
    append,
    float_try
)


def run_auto_briefing_loop():
    """
    genie_data_v5 → genie_briefing_log 자동 브리핑 생성
    """

    try:
        # ---------------------------------------
        # 1) genie_data_v5 최신 데이터 읽기
        # ---------------------------------------
        result = read_range("genie_data_v5!A:Z")
        values = result.get("values", [])

        if not values or len(values) < 2:
            return {"error": "No data rows"}

        headers = values[0]
        last = values[-1]

        def get_val(col):
            """컬럼명이 존재하면 해당 값을 반환"""
            if col in headers:
                idx = headers.index(col)
                return last[idx] if idx < len(last) else ""
            return ""

        # --- 지표 추출 ---
        btc_rsi = float_try(get_val("RSI(1h)"))
        btc_price = float_try(get_val("BTC/USD"))
        dominance = float_try(get_val("Dominance(%)"))
        mvrv_z = float_try(get_val("MVRV_Z"))
        fng_now = float_try(get_val("FNG"))
        market_code = get_val("MarketCode") or "BTC_USDT"

        # ---------------------------------------
        # 2) Briefing ID 생성
        # ---------------------------------------
        now_tag = datetime.now().strftime("%Y-%m-%d-%H:%M")
        briefing_id = f"B01.2.{random.randint(1000, 9999)}.{now_tag}"

        # ---------------------------------------
        # 3) Interpretation Code 계산
        # ---------------------------------------
        def get_interpretation_code(rsi, dom, fng):
            try:
                if rsi is None:
                    return "UNKNOWN"
                if rsi >= 70:
                    return "OVERHEAT"
                if rsi <= 30:
                    return "OVERSOLD"
                if (fng is not None and fng < 30) and rsi > 50:
                    return "FEAR_BUY"
                if rsi > 60 and dom < 55:
                    return "BULL_PREP"
                if rsi < 40 and dom > 55:
                    return "BEAR_PRESSURE"
                return "SIDEWAY"
            except:
                return "UNKNOWN"

        interpretation = get_interpretation_code(btc_rsi, dominance, fng_now)

        # ---------------------------------------
        # 4) confidence / meta_score
        # ---------------------------------------
        confidence = 0
        if btc_rsi is not None:
            confidence = max(0, min(100, 100 - abs(50 - btc_rsi)))

        meta_score = None
        if None not in (btc_rsi, dominance, mvrv_z):
            meta_score = round(
                (btc_rsi * 0.4 +
                 (100 - abs(56 - dominance)) * 0.3 +
                 (100 - abs(0 - mvrv_z)) * 0.3),
                2
            )

        # ---------------------------------------
        # 5) reference_key 생성
        # ---------------------------------------
        reference_key = f"C01.1.{briefing_id.split('.')[2]}.{briefing_id.split('.')[3]}"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ---------------------------------------
        # 6) 시트 기록 (genie_briefing_log)
        # A~K 11개 열
        # ---------------------------------------
        row_data = [[
            briefing_id,         # A
            timestamp,           # B
            market_code,         # C
            btc_rsi,             # D
            btc_price,           # E
            dominance,           # F
            mvrv_z,              # G
            interpretation,      # H
            confidence,          # I
            meta_score,          # J
            reference_key        # K
        ]]

        append("genie_briefing_log!A:K", row_data)

        return {
            "result": "logged",
            "Briefing_ID": briefing_id,
            "Interpretation": interpretation
        }

    except Exception as e:
        print("❌ auto_briefing_loop error:", e)
        return {"error": str(e)}
