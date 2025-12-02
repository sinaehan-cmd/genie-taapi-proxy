import requests

# Dominance 저장 버퍼 (24개 = 24시간 기준)
DOM_BUFFER = []
MAX_LEN = 24


# ------------------------------
# 1) 실시간 도미넌스 백업 API 3종
# ------------------------------
def fetch_primary():
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/global",
            timeout=8
        ).json()
        return round(r["data"]["market_cap_percentage"]["btc"], 2)
    except:
        return None


def fetch_backup():
    try:
        r = requests.get(
            "https://api.coinpaprika.com/v1/global",
            timeout=8
        ).json()
        btc = r.get("bitcoin_market_cap_usd")
        total = r.get("market_cap_usd_global")
        if btc and total:
            return round((btc / total) * 100, 2)
        return None
    except:
        return None


def fetch_coinstats():
    try:
        r = requests.get(
            "https://api.coinstats.app/public/v1/global",
            timeout=8
        ).json()
        return round(float(r.get("bitcoinDominance")), 2)
    except:
        return None


# ------------------------------
# 2) 실시간 Dominance 최종 결정
# ------------------------------
def get_realtime_dominance():
    for fn in [fetch_primary, fetch_backup, fetch_coinstats]:
        v = fn()
        if v is not None:
            return v
    return None


# ------------------------------
# 3) 버퍼 업데이트
# ------------------------------
def update_buffer(v):
    if v is None:
        return
    DOM_BUFFER.append(v)
    if len(DOM_BUFFER) > MAX_LEN:
        DOM_BUFFER.pop(0)


# ------------------------------
# 4) 4h / 1d Dominance 계산
# ------------------------------
def calc_dom_4h():
    if len(DOM_BUFFER) < 4:
        return None
    return round(sum(DOM_BUFFER[-4:]) / 4, 2)


def calc_dom_1d():
    if len(DOM_BUFFER) < 24:
        return None
    return round(sum(DOM_BUFFER[-24:]) / 24, 2)


# ------------------------------
# 5) Render 주는 패킷
# ------------------------------
def get_dominance_packet():
    now_dom = get_realtime_dominance()
    update_buffer(now_dom)

    return {
        "dom": now_dom,
        "dom4h": calc_dom_4h(),
        "dom1d": calc_dom_1d()
    }
