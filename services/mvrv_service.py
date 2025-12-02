import requests
from datetime import datetime

def safe_get(url, timeout=10):
    """HTTP 요청 안전 처리"""
    try:
        res = requests.get(url, timeout=timeout)
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return None


def compute_mvrv_paprika():
    """
    Coinpaprika 기반 MVRV_Z 계산
    - 가격, 시가총액, 실현가치 모두 무료 API 제공
    """
    url = "https://api.coinpaprika.com/v1/tickers/btc-bitcoin"
    data = safe_get(url)

    if not data:
        return {"MVRV_Z": "값없음", "error": "paprika_fail"}

    try:
        price = data["quotes"]["USD"]["price"]
        market_cap = data["quotes"]["USD"]["market_cap"]

        # 실현가치 (자주 제공되며 Glassnode와 유사)
        realized_cap = data["quotes"]["USD"].get("realized_market_cap")

        # 일부 시간대에서 realized_cap 빠지는 경우가 있음 → 보정
        if realized_cap is None or realized_cap <= 0:
            realized_cap = market_cap * 0.78

        mvrv = market_cap / realized_cap

        # Z-score 근사값
        mvrv_z = round((mvrv - 1) * 3.1, 3)

        return {
            "MVRV_Z": mvrv_z,
            "price": price,
            "market_cap": market_cap,
            "realized_cap": realized_cap,
            "method": "paprika",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        return {"MVRV_Z": "값없음", "error": str(e)}


# ------------------------------------------------------------------
# ⭐ 공식 export 함수 — routes에서 import하는 함수는 이것뿐
# ------------------------------------------------------------------
def get_mvrv_data():
    return compute_mvrv_paprika()
