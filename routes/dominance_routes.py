from flask import Blueprint, jsonify
from services.market_service import dominance_snapshot

bp = Blueprint("dominance_routes", __name__)

@bp.route("/dominance/snapshot")
def dom_snap():
    return jsonify(dominance_snapshot())

# Apps Script v9.1 호환
@bp.route("/dominance/packet")
def dom_packet():
    return jsonify(dominance_snapshot())
