# -*- coding: utf-8 -*-
# ======================================================
# 🤖 Genie Auto Loop — FIXED (No localhost, full remote calls)
# ======================================================

import requests, os, datetime, time
from flask import Blueprint, jsonify

bp = Blueprint("auto_loop", __name__)

GENIE_ACCESS_KEY = os.getenv("GENIE_ACCESS_KEY")
RENDER_BASE_URL = os.getenv("RENDER_BASE_URL", "https://genie-taapi-proxy-1.onrender.com")


def safe_post(endpoint: str):
    """Render 서버로 POST 전송 (내부 localhost 호출 제거 버전)"""
    url = f"{RENDER_BASE_URL}/{endpoint}"
    try:
        res = requests.post(url, json={"access_key": GENIE_ACCESS_KEY}, timeout=20)
        if res.status_code == 200:
            return True, res.json()
        return False, {"status": res.status_code, "text": res.text}
    except Exception as e:
        return False, {"error": str(e)}


@bp.route("/auto_loop", methods=["GET", "POST"])
def auto_loop():
    """📌 auto_loop 전체 루프를 안전하게 Render 엔드포인트로 호출하도록 정리한 공식 버전"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n🔥 [auto_loop] 시작: {now}")

    sequence = [
        "prediction_loop",
        "gti_loop",
        "learning_loop",
        "auto_gti_loop",
        "dominance/snapshot",
        "mvrv"
    ]

    results = {}

    for endpoint in sequence:
        ok, res = safe_post(endpoint)
        results[endpoint] = res
        time.sleep(2)   # 안정화용

    print("🔚 auto_loop 완료")
    return jsonify({
        "timestamp": now,
        "results": results
    })

