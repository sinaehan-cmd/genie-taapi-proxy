from flask import Blueprint, jsonify
from services.dominance_service import get_dominance_packet

bp = Blueprint("dominance", __name__)

@bp.route("/dominance/packet", methods=["GET"])
def dominance_packet():
    return jsonify(get_dominance_packet())
