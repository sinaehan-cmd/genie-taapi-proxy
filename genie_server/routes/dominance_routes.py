# ============================================================
# 🌐 Genie Server – Dominance Routes (Full Stable Version)
# ============================================================

from flask import Blueprint, jsonify
from genie_server.utils.dominance_fetcher import (
    get_current_dominance,
    get_avg,
    add_snapshot
)

bp = Blueprint("dominance", __name__, url_prefix="/dominance")


# ------------------------------------------------------------
# 1) 현재 Dominance 단일 조회
# ------------------------------------------------------------
@bp.route("/current", methods=["GET"])
def dominance_current():
    value = get_current_dominance()
    return jsonify({
        "dominance": value if value is not None else "값없음"
    })


# ------------------------------------------------------------
# 2) 최근 4시간 평균
# ------------------------------------------------------------
@bp.route("/avg/4h", methods=["GET"])
def dominance_avg_4h():
    avg4 = get_avg(4)
    return jsonify({
        "dominance_4h": avg4 if avg4 is not None else "값없음"
    })


# ------------------------------------------------------------
# 3) 최근 24시간 평균
# ------------------------------------------------------------
@bp.route("/avg/24h", methods=["GET"])
def dominance_avg_24h():
    avg24 = get_avg(24)
    return jsonify({
        "dominance_24h": avg24 if avg24 is not None else "값없음"
    })


# ------------------------------------------------------------
# 4) 30분마다 스냅샷 저장 (스케줄러가 주기적으로 호출)
# ------------------------------------------------------------
@bp.route("/snapshot", methods=["GET"])
def dominance_snapshot():
    ok = add_snapshot()
    return jsonify({
        "saved": ok
    })


# ------------------------------------------------------------
# 5) Apps Script에서 요구하는 통합 패킷 (핵심)
#    → GenieCollector v9.0이 호출하는 API
# ------------------------------------------------------------
@bp.route("/packet", methods=["GET"])
def dominance_packet():
    cur = get_current_dominance()
    avg4 = get_avg(4)
    avg24 = get_avg(24)

    return jsonify({
        "dom": cur if cur is not None else "값없음",
        "dom4h": avg4 if avg4 is not None else "값없음",
        "dom1d": avg24 if avg24 is not None else "값없음",
        "source": "genie_server",
        "status": "ok"
    })
