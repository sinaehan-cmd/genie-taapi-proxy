import requests

def dominance_snapshot():
    """
    BTC Dominance, 4h, 1d 값을 반환하는 Snapshot 함수
    Render Apps Script v9.1에서 사용하는 포맷 그대로 맞춤
    """
    try:
        r = requests.get("https://api.coingecko.com/api/v3/global", timeout=5)
        if r.status_code != 200:
            return {"dom": "값없음", "dom4h": "값없음", "dom1d": "값없음"}

        data = r.json()
        dom = data["data"]["market_cap_percentage"]["btc"]
        dom = round(dom, 2)

        return {
            "dom": dom,
            "dom4h": dom,   # 현재는 같은 값 사용 (4h 계산은 수동)
            "dom1d": dom
        }

    except:
        return {
            "dom": "값없음",
            "dom4h": "값없음",
            "dom1d": "값없음"
        }
