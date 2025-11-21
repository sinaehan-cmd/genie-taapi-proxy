import requests

COINANK_API_KEY = "b45efbbdf12b4294b1d33757c93febd7"

def get_mvrv_z():
    """
    CoinAnk MVRV_Z GET
    최신값 1개만 반환 (null도 허용해서 값없음 처리)
    """
    url = "https://open-api.coinank.com/api/indicator/index/charts?type=mvrv-zscore"
    headers = {
        "apikey": COINANK_API_KEY
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()

        # API 에러 처리
        if not data.get("success", False):
            print(f"❌ CoinAnk API Error: code={data.get('code')}")
            return "값없음"

        rows = data.get("data", [])

        if not rows:
            return "값없음"

        latest = rows[-1]   # MOST RECENT ROW
        value = latest.get("value")

        if value is None or value == "":
            return "값없음"

        return float(value)

    except Exception as e:
        print("❌ MVRV Fetch Error:", e)
        return "값없음"
