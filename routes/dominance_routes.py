from flask import Blueprint, jsonify
from services.dominance_service import get_dominance_packet

bp = Blueprint("dominance", __name__)

@bp.route("/dominance/packet", methods=["GET"])
def dominance_packet():
    """4h / 1d 포함 Dominance 패킷 반환"""
    pkt = get_dominance_packet()
    return jsonify(pkt)
