# genie_server/utils/dominance_fetcher.py

import os, json, time
import requests

DOM_LOG_PATH = "/opt/render/project/src/genie_server/utils/dominance_log.json"
COINGECKO_URL = "https://api.coingecko.com/api/v3/global"

def get_current_dominance():
    """현재 BTC dominance 1회 조회"""
    try:
        r = requests.get(COINGECKO_URL, timeout=10)
        data = r.json()
        return float(data["data"]["market_cap_percentage"]["btc"])
    except:
        return None

def load_log():
    if not os.path.exists(DOM_LOG_PATH):
        return []
    try:
        with open(DOM_LOG_PATH, "r") as f:
            return json.load(f)
    except:
        return []

def save_log(log):
    with open(DOM_LOG_PATH, "w") as f:
        json.dump(log, f)

def add_snapshot():
    """30분마다 dominance 스냅샷 저장"""
    value = get_current_dominance()
    if value is None:
        return False

    log = load_log()
    log.append({"ts": int(time.time()), "dominance": value})

    # 최근 48개만 유지 (24시간)
    log = log[-48:]

    save_log(log)
    return True

def get_avg(hours):
    """최근 N시간 평균 (hours=4 or 24)"""
    log = load_log()
    if not log:
        return None

    need = int((hours * 60) / 30)   # 4h=8개, 24h=48개
    samples = log[-need:]

    if not samples:
        return None

    vals = [x["dominance"] for x in samples if "dominance" in x]
    if not vals:
        return None

    return round(sum(vals) / len(vals), 2)
