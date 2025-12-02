import requests
import os

SHEET_JSON_URL = "https://genie-taapi-proxy-1.onrender.com/view-json/genie_data_v5"

def fetch_recent_dominance_values(limit=24):
    """Google Sheet JSON에서 최근 dominance(1h) 데이터 24개 불러오기"""
    try:
        r = requests.get(SHEET_JSON_URL, timeout=5).json()

        dominance_values = []
        for row in r.get("data", []):
            dom = row.get("Dominance(%)")
            if dom and isinstance(dom, (int, float)):
                dominance_values.append(dom)

        # 최신 값부터 정렬
        dominance_values = dominance_values[-limit:]

        return dominance_values

    except Exception as e:
        print("❌ Dominance fetch error:", e)
        return []


def calc_dominance_4h():
    values = fetch_recent_dominance_values(4)
    if len(values) < 4:
        return None
    return sum(values) / len(values)


def calc_dominance_1d():
    values = fetch_recent_dominance_values(24)
    if len(values) < 24:
        return None
    return sum(values) / len(values)
