# ============================================================
# Genie System – Dominance Fetcher (Stable Multi-Source Version)
# ============================================================

import os, json, time
import requests

DOM_LOG_PATH = "/opt/render/project/src/genie_server/utils/dominance_log.json"


def _fetch_json(url, timeout=10):
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


# ------------------------------------------------------------
# 1) Coingecko (2024–2025)
# ------------------------------------------------------------
def _get_from_coingecko():
    data = _fetch_json("https://api.coingecko.com/api/v3/global")
    try:
        return float(data["data"]["market_cap_percentage"]["btc"])
    except:
        return None


# ------------------------------------------------------------
# 2) CoinPaprika
# ------------------------------------------------------------
def _get_from_paprika():
    data = _fetch_json("https://api.coinpaprika.com/v1/global")
    try:
        return float(data["bitcoin_dominance_percentage"])
    except:
        return None


# ------------------------------------------------------------
# 3) CoinStats
# ------------------------------------------------------------
def _get_from_coinstats():
    data = _fetch_json("https://api.coinstats.app/public/v1/global")
    try:
        return float(data.get("btcDominance") or data.get("bitcoinDominance"))
    except:
        return None


# ------------------------------------------------------------
# ⭐ Public: 현재 Dominance 조회
# ------------------------------------------------------------
def get_current_dominance():
    for fn in [_get_from_coingecko, _get_from_paprika, _get_from_coinstats]:
        v = fn()
        if v is not None:
            return v
    return None


# ------------------------------------------------------------
# Snapshot Log (30분)
# ------------------------------------------------------------
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
    value = get_current_dominance()
    if value is None:
        return False

    log = load_log()
    log.append({"ts": int(time.time()), "dominance": value})
    log = log[-48:]  # 최근 24시간

    save_log(log)
    return True


# ------------------------------------------------------------
# 평균 계산
# ------------------------------------------------------------
def get_avg(hours):
    log = load_log()
    if not log:
        return None

    need = int((hours * 60) / 30)
    samples = log[-need:]

    vals = [x.get("dominance") for x in samples if x.get("dominance") is not None]
    if not vals:
        return None

    return round(sum(vals) / len(vals), 2)
