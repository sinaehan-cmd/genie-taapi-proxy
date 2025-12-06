# services/reader_service.py
# Genie Reader Core — v9.3 완전 호환 버전

from services.sheet_service import read_sheet


def safe_float(v):
    try:
        return float(v)
    except:
        return None


def run_reader_core(limit=5):
    """
    Reader Core
    - genie_data_v5 최신 limit개 행을 읽어 구조화된 dict로 반환
    """
    rows = read_sheet("genie_data_v5")
    if not rows or len(rows) < 2:
        return {"status": "empty"}

    header = rows[0]       # 첫 행이 헤더
    data_rows = rows[1:]   # 실제 데이터

    # limit 만큼 뒤에서 가져오기
    recent = data_rows[-limit:]

    items = []

    for row in recent:
        item = {}

        def col(name, cast=False):
            if name not in header:
                return None
            idx = header.index(name)
            if idx >= len(row):
                return None
            return safe_float(row[idx]) if cast else row[idx]

        # 핵심 필드만 선택
        item["Timestamp"]       = col("기준시간")
        item["BTC_Price"]       = col("BTC/USD", cast=True)
        item["ETH_Price"]       = col("ETH/USD", cast=True)
        item["SOL_Price"]       = col("SOL/USD", cast=True)
        item["XRP_Price"]       = col("XRP/USD", cast=True)

        item["Dominance"]       = col("Dominance(%)", cast=True)
        item["Dominance_4h"]    = col("Dominance(4h)", cast=True)
        item["Dominance_1d"]    = col("Dominance(1d)", cast=True)

        item["RSI_1h"]          = col("RSI(1h)", cast=True)
        item["RSI_4h"]          = col("RSI(4h)", cast=True)
        item["RSI_1d"]          = col("RSI(1d)", cast=True)

        item["MVRV_Z"]          = col("MVRV_Z", cast=True)

        items.append(item)

    return {
        "status": "success",
        "count": len(items),
        "items": items
    }
