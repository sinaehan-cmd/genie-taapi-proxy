# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify
from genie_server.utils.dominance_fetcher import get_dominance
from genie_server.utils.google_sheets import append_row
from datetime import datetime

bp = Blueprint("dominance_routes", __name__)

@bp.route("/dominance/snapshot", methods=["POST"])
def dominance_snapshot():
    """도미넌스 값이 None이어도 서버 에러 없이 snapshot 로깅"""
    try:
        dom = get_dominance()

        # Fallback 처리
        if dom is None:
            dom = 0

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        append_row("genie_alert_log", [
            now, "DominanceSnapshot", dom
        ])

        return jsonify({
            "timestamp": now,
            "dominance": dom,
            "result": "success"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
