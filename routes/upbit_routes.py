# routes/upbit_routes.py
# Upbit Private API — Secure v2025.12

import os
import time
import uuid
import hashlib
import jwt
import requests
from flask import Blueprint, jsonify

upbit_bp = Blueprint("upbit_routes", __name__)

ACCESS_KEY = os.getenv("UPBIT_ACCESS_KEY")
SECRET_KEY = os.getenv("UPBIT_SECRET_KEY")
SERVER_URL = "https://api.upbit.com"


# ----------------------------------------
# JWT 생성
# ----------------------------------------
def make_authorization_token(query=None):
    payload = {
        "access_key": ACCESS_KEY,
        "nonce": str(uuid.uuid4())
    }

    # 쿼리 파라미터가 있으면 query_hash 포함
    if query:
        query_string = "&".join([f"{k}={v}" for k, v in query.items()])
        m = hashlib.sha512()
        m.update(query_string.encode("utf-8"))
        query_hash = m.hexdigest()

        payload["query_hash"] = query_hash
        payload["query_hash_alg"] = "SHA512"

    jwt_token = jwt.encode(payload, SECRET_KEY)
    authorization_token = f"Bearer {jwt_token}"

    return authorization_token


# ----------------------------------------
# ✔ TEST 1: API 정상 연결 테스트
# ----------------------------------------
@upbit_bp.route("/test/upbit/auth")
def test_auth():
    try:
        token = make_authorization_token()
        return jsonify({
            "status": "ok",
            "token_preview": token[:40] + "...",
            "message": "Upbit Auth Token generated successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ----------------------------------------
# ✔ TEST 2: 내 잔고 조회 (Private API)
# ----------------------------------------
@upbit_bp.route("/test/upbit/balance")
def balance():
    try:
        headers = {
            "Authorization": make_authorization_token()
        }

        res = requests.get(SERVER_URL + "/v1/accounts", headers=headers)
        res.raise_for_status()

        return jsonify(res.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500
