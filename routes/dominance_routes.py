from flask import Blueprint, jsonify
from services.market_service import dominance_snapshot

bp = Blueprint("dominance_routes", __name__)

@bp.route("/dominance/snapshot")
def dom_snap():
    """
    단순 도미넌스 스냅샷 (디버그 & 로그용)
    """
    data = dominance_snapshot()
    return jsonify(data)


# Apps Script v9.1 호환용
@bp.route("/dominance/packet")
def dom_packet():
    """
    Apps Script v9.1에서 사용하는 패킷 포맷
    genie_collector_v9_1에서 기대하는 구조:
      { "dom": ..., "dom4h": ..., "dom1d": ... }
    지금은 우선 3개 모두 동일 값으로 리턴 (4h/1d는 나중에 확장)
    """
    data = dominance_snapshot()
    dom = data.get("btc_dominance")

    return jsonify({
        "dom": dom,
        "dom4h": dom,
        "dom1d": dom,
    })
