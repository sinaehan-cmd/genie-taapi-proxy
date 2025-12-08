# services/upbit_service.py
# Upbit Public API Test Module

import requests

UPBIT_BASE = "https://api.upbit.com/v1"


def fetch_ticker(market="KRW-BTC"):
    """
    업비트 현재가(simple ticker) 조회
    """
    try:
        url = f"{UPBIT_BASE}/ticker?markets={market}"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def fetch_orderbook(market="KRW-BTC"):
    """
    업비트 호가 조회
    """
    try:
        url = f"{UPBIT_BASE}/orderbook?markets={market}"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def fetch_market_list():
    """
    업비트 전체 마켓 조회
    """
    try:
        url = f"{UPBIT_BASE}/market/all"
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}
