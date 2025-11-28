# -*- coding: utf-8 -*-
# ======================================================
# 📗 Reader Loop — 최소 기능(헬스체크 + 성공 리턴)
# ======================================================

from flask import Blueprint, jsonify
import datetime

bp = Blueprint("reader_loop", __name__)

@bp.route("/reader_loop", methods=["GET", "POST"])
def reader_loop():
    """
    Render auto_loop가 호출할 때 반드시 200을 반환해야 하는 엔드포인트.
    실제 로직은 필요 없음. 헬스 체크 역할.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return jsonify({
        "timestamp": now,
        "status": "ok",
        "message": "reader_loop alive"
    })
