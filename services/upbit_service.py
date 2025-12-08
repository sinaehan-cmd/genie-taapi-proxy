# loops/gpt_briefing_loop.py
import json
from services.sheet_service import read_sheet, append_row
from services.gpt_client import call_gpt_briefing  # GPT API 래퍼 (네 키 사용)

BRIEFING_SHEET = "genie_briefing_log"
DATA_SHEET = "genie_data_v5"

def run_gpt_briefing_loop():
    """
    1) genie_data_v5에서 마지막 1줄 읽기
    2) GPT로 해석 요청
    3) 결과를 genie_briefing_log에 append
    """
    data = read_sheet(DATA_SHEET)
    if not data or len(data) < 2:
        return {"error": "no data"}

    header = data[0]
    last_row = data[-1]
    row_dict = {header[i]: last_row[i] for i in range(len(header))}

    # 2) GPT에 넘길 입력 패키지 구성
    payload = {
        "timestamp": row_dict.get("기준시간"),
        "btc_price": row_dict.get("BTC/USD"),
        "eth_price": row_dict.get("ETH/USD"),
        "sol_price": row_dict.get("SOL/USD"),
        "xrp_price": row_dict.get("XRP/USD"),
        "rsi_1h": row_dict.get("RSI(1h)"),
        "rsi_4h": row_dict.get("RSI(4h)"),
        "rsi_1d": row_dict.get("RSI(1d)"),
        "dom_now": row_dict.get("Dominance(%)"),
        "dom_4h": row_dict.get("Dominance(4h)"),
        "dom_1d": row_dict.get("Dominance(1d)"),
        "mvrv_z": row_dict.get("MVRV_Z"),
        "fng": row_dict.get("FNG"),
    }

    gpt_result = call_gpt_briefing(payload)
    # gpt_result는 아래처럼 JSON으로 받아온다고 가정:
    # {
    #   "MarketCode": "BTC_USDT",
    #   "BTC_RSI": 43.8,
    #   "BTC_Price": 89368.83,
    #   "Dominance": 55.97,
    #   "MVRV_Z": 0,
    #   "Interpretation": "SIDEWAY",
    #   "Confidence": 91.6,
    #   "Reference": "C01.1.xxx...",
    #   "Comment": "단기 조정 / 중기 관망"
    # }

    # 3) 시트에 로그 남기기 (컬럼 순서는 genie_briefing_log 정의에 맞게)
    row_to_append = [
        gpt_result.get("Timestamp", payload["timestamp"]),
        gpt_result.get("MarketCode", "BTC_USDT"),
        gpt_result.get("BTC_Price", payload["btc_price"]),
        gpt_result.get("BTC_RSI", payload["rsi_1h"]),
        gpt_result.get("Dominance", payload["dom_now"]),
        gpt_result.get("MVRV_Z", payload["mvrv_z"]),
        gpt_result.get("Interpretation"),
        gpt_result.get("Confidence"),
        gpt_result.get("Reference"),
        gpt_result.get("Comment"),
    ]

    append_row(BRIEFING_SHEET, row_to_append)

    return {
        "status": "ok",
        "payload": payload,
        "gpt_result": gpt_result,
    }
