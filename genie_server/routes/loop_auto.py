import requests, os, datetime, time, threading
from flask import Blueprint, jsonify

bp = Blueprint("auto_loop", __name__)

GENIE_ACCESS_KEY = os.getenv("GENIE_ACCESS_KEY")
RENDER_BASE_URL = os.getenv("RENDER_BASE_URL", "https://genie-taapi-proxy-1.onrender.com")

def safe_post(endpoint: str):
    url = f"{RENDER_BASE_URL}/{endpoint}"
    try:
        res = requests.post(url, json={"access_key": GENIE_ACCESS_KEY}, timeout=15)
        if res.status_code == 200:
            return True, res.json()
        return False, {"status": res.status_code, "text": res.text}
    except Exception as e:
        return False, {"error": str(e)}

def background_loop():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n🔥 [auto_loop] 백그라운드 시작: {now}")

    sequence = [
        "prediction_loop",
        "gti_loop",
        "learning_loop",
        "auto_gti_loop",
        "dominance/snapshot",
        "mvrv"
    ]

    for ep in sequence:
        ok, res = safe_post(ep)
        print(f" → {ep} OK={ok}")
        time.sleep(1)

    print("🔚 auto_loop 백그라운드 완료")

@bp.route("/auto_loop", methods=["GET", "POST"])
def auto_loop():
    threading.Thread(target=background_loop).start()
    return jsonify({
        "status": "started",
        "message": "auto_loop is running in background"
    })
