# routes/dominance_routes.py

from flask import Blueprint, jsonify
from services.market_service import dominance_snapshot

bp = Blueprint("dominance_routes", __name__)


# --------------------------------------------------------
# 1) 기본 스냅샷 API (Genie internal)
# --------------------------------------------------------
@bp.route("/dominance/snapshot")
def dom_snap():
    """Return the latest dominance snapshot."""
    data = dominance_snapshot()   # dict 형태
    return jsonify(data), 200


# --------------------------------------------------------
# 2) Apps Script v9.1 패킷 버전
# Google Apps Script fetch()에서 바로 읽기 가능하게 구성
# --------------------------------------------------------
@bp.route("/dominance/packet")
def dom_packet():
    """
    Apps Script 전용 패킷.
    반환 형식:
    {
        "status": "success",
        "payload": { ... dominance data ... }
    }
    """
    data = dominance_snapshot()
    packet = {
        "status": "success",
        "payload": data,
        "source": "genie_server_v2",
        "type": "dominance_packet"
    }
    return jsonify(packet), 200
