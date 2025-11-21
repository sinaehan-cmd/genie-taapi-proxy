import requests
import re
import json

TV_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tradingview.com/"
}

def get_mvrv_z():
    """
    TradingView 기반 고정밀 MVRV_Z 크롤러 (업데이트 버전)
    widget JSON 구조 변화 대비
    """
    try:
        url = "https://www.tradingview.com/symbols/BTCUSD/technicals/"
        html = requests.get(url, headers=TV_HEADERS, timeout=10).text

        # 1) "data" 또는 "sectionData" 또는 "technicals" 모두 탐색
        pattern_list = [
            r'"data":\s*({.*?})\s*,\s*"columns"',
            r'"sectionData":\s*({.*?})\s*,\s*"columns"',
            r'"technicals":\s*({.*?})\s*,\s*"tab"'
        ]

        match = None
        for p in pattern_list:
            match = re.search(p, html, re.S)
            if match:
                break

        if not match:
            print("❌ JSON block not found in TradingView HTML")
            return "값없음"

        widget_json = json.loads(match.group(1))

        # 2) 심볼 리스트 안에서 MVRV 관련 항목 찾기
        symbols = widget_json.get("symbols", [])
        script_id = None

        for item in symbols:
            name = item.get("name", "").upper()
            if "MVRV" in name:
                script_id = item.get("id")
                break

        if not script_id:
            print("❌ MVRV script id not found")
            return "값없음"

        # 3) TradingView scanner API 요청
        tv_api_url = "https://scanner.tradingview.com/crypto/scan"
        payload = {
            "symbols": {"tickers": ["BINANCE:BTCUSDT"], "query": {"types": []}},
            "columns": [f"technical.{script_id}"]
        }

        res = requests.post(tv_api_url, json=payload, headers=TV_HEADERS, timeout=10)
        data = res.json()

        items = data.get("data", [])
        if not items or "d" not in items[0]:
            return "값없음"

        mvrv = items[0]["d"][0]
        return float(mvrv) if mvrv is not None else "값없음"

    except Exception as e:
        print("❌ MVRV Fetch Error:", e)
        return "값없음"
