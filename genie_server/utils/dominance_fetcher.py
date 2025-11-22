import os, json, time
import requests

# ---------------------------------------------------------
# 저장 경로
# ---------------------------------------------------------
DOM_LOG_PATH = "/opt/render/project/src/genie_server/utils/dominance_log.json"

# API URLs
COINGECKO_URL = "https://api.coingecko.com/api/v3/global"
PAPRIKA_URL = "https://api.coinpaprika.com/v1/global"
COINSTATS_URL = "https://api.coinstats.app/public/v1/global"


# ---------------------------------------------------------
# 기본 fetch 함수
# ---------------------------------------------------------
def _fetch_json(url, timeout=10):
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None


# ---------------------------------------------------------
# 1회 도미넌스 조회 (failover 3단계)
# ---------------------------------------------------------
def get_current_dominance():
    """현재 dominance 값 반영 — Coingecko → Paprika → CoinStats"""

    # 1) Coingecko
    cg = _fetch_json(COINGECKO_URL)
    try:
        d = cg["data"]["market_cap_percentage"]["btc"]
        return float(d)
    except:
        pass

    # 2) Paprika
    pk = _fetch_json(PAPRIKA_URL)
    try:
        mc = pk["market_cap_usd_global"]
        btc_mc = pk["bitcoin_market_cap_usd"]
        if mc and btc_mc:
            return float((btc_mc / mc) * 100)
    except:
        pass

    # 3) CoinStats
    cs = _fetch_json(COINSTATS_URL)
    try:
        d = cs["bitcoinDominance"]
        return float(d)
    except:
        pass

    return None  # 실패


# ---------------------------------------------------------
# 로그 로드 & 저장
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# 30분 snapshot
# ---------------------------------------------------------
def add_snapshot():
    """30분마다 dominance 스냅샷 저장"""
    value = get_current_dominance()
    if value is None:
        return False

    log = load_log()
    log.append({"ts": int(time.time()), "dominance": value})

    # 최근 48개 유지 (24시간)
    log = log[-48:]

    save_log(log)
    return True


# ---------------------------------------------------------
# 평균 계산 (4h, 1d)
# ---------------------------------------------------------
def get_avg(hours):
    """
    최근 hours 시간 동안의 평균.
    4h → 8개 (30분 단위)
    24h → 48개
    """
    log = load_log()
    if not log:
        return None

    need = int((hours * 60) / 30)
    samples = log[-need:]

    vals = [x["dominance"] for x in samples if x.get("dominance")]

    if not vals:
        return None

    return round(sum(vals) / len(vals), 2)


# ---------------------------------------------------------
# 최종 통합: 현재 + 4h + 1d
# ---------------------------------------------------------
def get_dominance_packet():
    """
    Apps Script에서 사용할 최종 패킷 생성
    - dominance
    - dominance_4h
    - dominance_1d
    """

    # 1) 실시간
    current = get_current_dominance()

    # 2) snapshot 기반 평균
    avg_4h = get_avg(4)
