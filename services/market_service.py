
import requests

def get_usd_krw():
    try:
        r = requests.get("https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD").json()
        return r[0]["basePrice"]
    except:
        return None

def get_fng_index():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1").json()
        return r["data"][0]["value"]
    except:
        return None
