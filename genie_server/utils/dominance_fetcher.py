# genie_server/utils/dominance_fetcher.py
import requests

# 1️⃣ CoinGecko
def fetch_from_coingecko():
    try:
        url = "https://api.coingecko.com/api/v3/global"
        r = requests.get(url, timeout=10).json()
        return round(r["data"]["market_cap_percentage"]["btc"], 2)
    except:
        return None

# 2️⃣ CoinMarketCap
def fetch_from_cmc(api_key):
    try:
        if not api_key:
            return None
        url = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
        r = requests.get(url, headers={"X-CMC_PRO_API_KEY": api_key}, timeout=10).json()
        return round(r["data"]["btc_dominance"], 2)
    except:
        return None

# 3️⃣ TradingView HTML 파싱
def fetch_from_tradingview():
    try:
        url = "https://www.tradingview.com/markets/cryptocurrencies/global-charts/"
        html = requests.get(url, timeout=10).text
        # TradingView dominance keyword
        marker = '"dominance":{"btc":'
        if marker in html:
            part = html.split(marker)[1]
            value = part.split(",")[0]
            return round(float(value), 2)
        return None
    except:
        return None

# 4️⃣ 직접 계산 (fallback)
def compute_manual_dominance():
    try:
        global_data = requests.get(
            "https://api.coingecko.com/api/v3/global", timeout=10
        ).json()

        total_cap = global_data["data"]["total_market_cap"]["usd"]

        btc_price = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_market_cap=true",
            timeout=10
        ).json()["bitcoin"]["usd"]

        btc_cap = requests.get(
            "https://api.coingecko.com/api/v3/coins/bitcoin",
            timeout=10
        ).json()["market_data"]["market_cap"]["usd"]

        return round((btc_cap / total_cap) * 100, 2)
    except:
        return None


# 🧠 Master failover
def fetch_dominance(api_key_cmc=None):
    for method in [
        fetch_from_coingecko,
        lambda: fetch_from_cmc(api_key_cmc),
        fetch_from_tradingview,
        compute_manual_dominance
    ]:
        value = method()
        if value:
            return value
    return None
