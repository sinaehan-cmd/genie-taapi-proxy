import requests

DOM_BUFFER = []
MAX_LEN = 24

# ------------------------------
# 1) Coingecko
# ------------------------------
def fetch_primary():
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/global",
            timeout=6
        ).json()
        # 구조가 맞으면:
        v = r["data"]["market_cap_percentage"]["btc"]
        return round(float(v), 2)
    except:
        return None

# ------------------------------
# 2) Coinpaprika — 정상 동작 버전
# ------------------------------
def fetch_backup():
    try:
        r = requests.get(
            "https://api.coinpaprika.com/v1/global",
            timeout=6
        ).json()

        # coinpaprika는 이미 도미넌스 값 자체를 제공한다!
        v = r.get("bitcoin_dominance_percentage")
        if v is None:
            return None
        
        return round(float(v), 2)
    except:
        return None

# ------------------------------
# 3) 제거 — Coinstats는 폐기됨
# ------------------------------
def get_realtime_dominance():
    for fn in [fetch_primary, fetch_backup]:
        v = fn()
        if v is not None:
            return v
    return None

# 버퍼 업데이트
def update_buffer(v):
    if v is None:
        return
    DOM_BUFFER.append(v)
    if len(DOM_BUFFER) > MAX_LEN:
        DOM_BUFFER.pop(0)

# 4h 계산
def calc_dom_4h():
    if len(DOM_BUFFER) < 4:
        return None
    return round(sum(DOM_BUFFER[-4:]) / 4, 2)

# 1d 계산
def calc_dom_1d():
    if len(DOM_BUFFER) < 24:
        return None
    return round(sum(DOM_BUFFER[-24:]) / 24, 2)

# 최종 패킷
def get_dominance_packet():
    now_dom = get_realtime_dominance()
    update_buffer(now_dom)

    return {
        "dom": now_dom,
        "dom4h": calc_dom_4h(),
        "dom1d": calc_dom_1d()
    }
