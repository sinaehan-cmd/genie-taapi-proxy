from flask import Blueprint, jsonify
from services.mvrv_service import calculate_mvrv_z

bp = Blueprint("mvrv", __name__)

@bp.route("/mvrv_z")
def mvrv_z_api():
    value, msg = calculate_mvrv_z()
    return jsonify({"mvrv_z": value, "source": msg})
