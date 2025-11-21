from flask import Blueprint, jsonify
from utils.mvrv_fetcher import get_mvrv_z

bp = Blueprint("mvrv_route", __name__)

@bp.route("/mvrv_test")
def mvrv_test():
    return jsonify({
        "MVRV_Z": get_mvrv_z()
    })
