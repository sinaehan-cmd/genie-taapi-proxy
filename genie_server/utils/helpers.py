from datetime import datetime
import random

def float_try(v, default=0.0):
    try:
        if v is None or str(v).strip() == "":
            return default
        return float(v)
    except:
        return default

def safe_float(x):
    try:
        if x in ["", None, "값없음", "N/A", "-", "null"]:
            return None
        return float(x)
    except Exception:
        return None

def generate_briefing_id():
    now = datetime.now().strftime("%Y-%m-%d-%H:%M")
    return f"B01.2.{random.randint(1000,9999)}.{now}"
