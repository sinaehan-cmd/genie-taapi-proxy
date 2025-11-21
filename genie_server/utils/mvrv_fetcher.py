import requests
import re
import json

TV_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tradingview.com/"
}

def get_mvrv_z():
    """
    TradingView 기반 고정밀 MVRV_Z 크롤러
    Glassnode 기반 지표와 동일 구조
    """
    try:
        # 1) TradingView 지표 페이지 HTML 로드
        url = "https://www.tradingview.com/symbols/BTCUSD/technicals/"
        html = requests.get(url, headers=TV_HEADERS, timeout=10).text

        # 2) 내부 지표 스크립트의 widget JSON 추출
        #    TradingView는 데이터를 아래 변수에 저장함: "data": {...} 형태
        match = re.search(r'"data":\s*({.*?})\s*,\s*"columns"', html, re.S)

        if not match:
            print("❌ TradingView widget JSON not found")
            return "값없음"

        widget_json = json.loads(match.group(1))

        # 3) 인기 지표 중 MVRV_Z 스크립트 ID 찾아내기
        indicators = widget_json.get("symbols", [])
        script_id = None

        for item in indicators:
            if "MVRV" in item.get("name", "").upper():
                script_id = item["id"]
                break

        if not script_id:
            print("❌ MVRV_Z script ID not found")
            return "값없음"

        # 4) TradingView 내부 JSON 엔드포인트로 요청
        tv_api_url = (
            "https://scanner.tradingview.com/crypto/scan"
        )

        payload = {
            "symbols": {"tickers": ["BINANCE:BTCUSDT"], "query": {"types": []}},
            "columns": [f"technical.{script_id}"]
        }

        res = requests.post(tv_api_url, json=payload, headers=TV_HEADERS, timeout=10)
        data = res.json()

        # 5) 최신 MVRV_Z 값 추출
        items = data.get("data", [])

        if not items or "d" not in items[0]:
            return "값없음"

        mvrv = items[0]["d"][0]

        if mvrv is None:
            return "값없음"

        return float(mvrv)

    except Exception as e:
        print("❌ MVRV_Z Fetch Error:", e)
        return "값없음"
