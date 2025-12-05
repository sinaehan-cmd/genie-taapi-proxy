# services/reader_service.py
# Reader Core — app(11).py 기반 복원 버전

from services.sheet_service import read_sheet


def run_reader_core(limit=5):
    """
    Reader Core
    - genie_data_v5에서 최근 limit개 행을 읽어서 정리
    """
    rows = read_sheet("genie_data_v5")

    if not rows:
        return {"status": "empty"}

    # 뒤에서 limit개 가져오기
    recent = rows[-limit:]

    parsed = []

    for r in recent:
        item = {
            "Timestamp": r.get("Timestamp"),
            "BTC_Price": _safe_float(r.get("BTC_Price")),
            "ETH_Price": _safe_float(r.get("ETH_Price")),
            "Dominance": _safe_float(r.get("Dominance")),
            "RSI": _safe_float(r.get("RSI")),
            "MVRV_Z": _safe_float(r.get("MVRV_Z")),
        }
        parsed.append(item)

    return {
        "status": "success",
        "count": len(parsed),
        "items": parsed
    }


def _safe_float(v):
    try:
        return float(v)
    except:
        return None
