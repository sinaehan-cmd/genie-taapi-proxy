import requests
import time

# Dominance 저장용 (최근 24개 — 24시간 가정)
DOM_BUFFER = []      # 최근 24개의 dominance 저장
MAX_LEN = 24


def fetch_primary():
    """1차 Dominance — CoinGecko"""
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/global",
            timeout=8
        ).json()
        return round(r["data"]["market_cap_percentage"]["btc"], 2)
    except:
        return None


def fetch_backup():
    """2차 Dominance — CoinPaprika"""
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
    """3차 Dominance — CoinStats"""
    try:
        r = requests.get(
            "https://api.coinstats.app/public/v1/global",
            timeout=8
        ).json()
        dom = r.get("bitcoinDominance")
        return round(float(dom), 2)
    except:
        return None


def get_realtime_dominance():
    """실시간 Dominance 3중 백업"""
    for func in [fetch_primary, fetch_backup, fetch_coinstats]:
        dom = func()
        if dom is not None:
            return dom
    return None


def update_buffer(new_value):
    """최근 24개 Dominance 저장"""
    if new_value is None:
        return

    DOM_BUFFER.append(new_value)
    if len(DOM_BUFFER) > MAX_LEN:
        DOM_BUFFER.pop(0)


def calc_dom_4h():
    """최근 4개의 Dominance 평균 = 4h Dominance"""
    if len(DOM_BUFFER) < 4:
        return None
    return round(sum(DOM_BUFFER[-4:]) / 4, 2)


def calc_dom_1d():
    """최근 24개의 Dominance 평균 = 1d Dominance"""
    if len(DOM_BUFFER) < 24:
        return None
    return round(sum(DOM_BUFFER[-24:]) / 24, 2)


def get_dominance_packet():
    """
    Render에서 Apps Script로 제공하는 Dominance Packet
    dom: 실시간 dominant
    dom4h: 지니 계산 Dominance(4h)
    dom1d: 지니 계산 Dominance(1d)
    """
    now_dom = get_realtime_dominance()
    update_buffer(now_dom)

    return {
        "dom": now_dom,
        "dom4h": calc_dom_4h(),
        "dom1d": calc_dom_1d(),
    }
