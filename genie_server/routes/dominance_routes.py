# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify
from datetime import datetime

# 수정된 부분: get_dominance → get_current_dominance 로 변경
from genie_server.utils.dominance_fetcher import get_current_dominance
from genie_server.utils.google_sheets import append_row

bp = Blueprint("dominance_routes", __name__)


@bp.route("/dominance/snapshot", methods=["POST"])
def dominance_snapshot():
    """
    최신 도미넌스 스냅샷을 Google Sheets에 기록
    """
    try:
        dom = get_current_dominance()

        # Fallback
        if dom is None:
            dom = 0

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        append_row("genie_alert_log", [
            now,
            "DominanceSnapshot",
            dom
        ])

        return jsonify({
            "timestamp": now,
            "dominance": dom,
            "result": "success"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
