# services/dominance_service.py
# Final Stable Version — Only provides current dominance(dom)
# Sheet-side handles 4h/1d calculations

import requests


def safe_fetch_json(url, timeout=6):
    """안정성 강화 JSON fetch"""
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ Dominance fetch error from {url} —", e)
        return None


# ----------------------------------------
# 1) Primary — CoinGecko
# ----------------------------------------
def fetch_primary():
    try:
        r = safe_fetch_json("https://api.coingecko.com/api/v3/global")
        if not r:
            return None

        v = r["data"]["market_cap_percentage"]["btc"]
        return round(float(v), 2)
    except:
        return None


# ----------------------------------------
# 2) Backup — Coinpaprika (dominance 제공)
# ----------------------------------------
def fetch_backup():
    try:
        r = safe_fetch_json("https://api.coinpaprika.com/v1/global")
        if not r:
            return None

        v = r.get("bitcoin_dominance_percentage")
        if v is None:
            return None

        return round(float(v), 2)
    except:
        return None


# ----------------------------------------
# 3) Combined realtime dominance fetcher
# ----------------------------------------
def get_realtime_dominance():
    for fetcher in [fetch_primary, fetch_backup]:
        v = fetcher()
        if v is not None:
            return v
    return None


# ----------------------------------------
# ⭐ 최종 API 출력 — ONLY 'dom'
# ----------------------------------------
def get_dominance_packet():
    dom = get_realtime_dominance()

    return {
        "dom": dom  # Apps Script가 4h/1d 자동 생성
    }
