# services/behavior_service.py
# Genie Behavior Engine v1.0
# action_log + data_v5 → behavior_log 자동 평가

from datetime import datetime
from services.sheet_service import read_range, append, float_try


def safe(v):
    """float 변환 보조 함수"""
    try:
        return float(v)
    except:
        return None


def load_latest_market():
    """
    genie_data_v5 마지막 행을 가져와 시장 상태를 구성한다.
    """
    rows = read_range("genie_data_v5!A:Z").get("values", [])
    if len(rows) < 2:
        return None

    header = rows[0]
    last = rows[-1]

    def g(col):
        return last[header.index(col)] if col in header else None

    return {
        "timestamp": g("기준시간"),
        "rsi": safe(g("RSI(1h)")),
        "dominance": safe(g("Dominance(%)")),
        "mvrvz": safe(g("MVRV_Z"))
    }


def load_latest_action():
    """
    genie_action_log 마지막 입력값을 가져온다.
    사용자가 수동 입력한 가장 최근 행동.
    """
    rows = read_range("genie_action_log!A:F").get("values", [])
    if len(rows) < 2:
        return None

    header = rows[0]
    last = rows[-1]

    def g(col):
        return last[header.index(col)] if col in header else None

    return {
        "timestamp": g("Timestamp"),
        "action": g("Action"),
        "symbol": g("Symbol"),
        "price": safe(g("Price")),
        "krw_value": safe(g("KRW_Value")),
        "reason": g("Reason")
    }


def evaluate_behavior(action, market):
    """
    지니가 행동의 질을 평가하는 core logic

    반환값:
    - action_quality
    - risk_level
    - notes
    - recommended_next
    """

    rsi = market["rsi"]
    dom = market["dominance"]
    mvrvz = market["mvrvz"]
    act = action["action"]
    price = action["price"]

    # --------------------------
    # 행동 평가 로직
    # --------------------------

    # 기본값
    quality = "NEUTRAL"
    risk = "MEDIUM"
    notes = []
    recommended = None

    # ---- BUY 평가 ----
    if act == "BUY":
        if rsi and rsi < 35:
            quality = "GOOD"
            notes.append("저RSI 구간 매수 — 통계적으로 우수")
        if rsi and rsi > 70:
            quality = "RISKY"
            risk = "HIGH"
            notes.append("과매수 구간에서 매수")
        if dom and dom > 58:
            notes.append("BTC 도미넌스 고점 — 알트 약세 구간일 수 있음")

        recommended = "HOLD & WAIT"

    # ---- SELL 평가 ----
    elif act == "SELL":
        if rsi and rsi > 65:
            quality = "GOOD"
            notes.append("고RSI 구간 매도")
        if rsi and rsi < 40:
            quality = "EARLY"
            risk = "HIGH"
            notes.append("저점 매도 위험")
        recommended = "WAIT_FOR_REBUY"

    # ---- 기타 ----
    else:
        notes.append("Unknown action type")

    return {
        "action_quality": quality,
        "risk_level": risk,
        "notes": "; ".join(notes),
        "recommended": recommended
    }


def write_behavior_log(action, market, eval_res):
    """
    genie_behavior_log에 기록
    """
    row = [[
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        action["action"],
        action["symbol"],
        action["price"],
        market["rsi"],
        market["dominance"],
        market["mvrvz"],
        eval_res["action_quality"],
        eval_res["risk_level"],
        eval_res["notes"],
        eval_res["recommended"]
    ]]

    append("genie_behavior_log!A:K", row)

    return row


def run_behavior_core():
    """
    Behavior Engine 전체 실행 (1회)
    """
    action = load_latest_action()
    market = load_latest_market()

    if action is None:
        return {"error": "No action_log data"}

    if market is None:
        return {"error": "No market data"}

    eval_res = evaluate_behavior(action, market)
    logged = write_behavior_log(action, market, eval_res)

    return {
        "status": "logged",
        "action": action,
        "market": market,
        "evaluation": eval_res,
        "row": logged
    }
