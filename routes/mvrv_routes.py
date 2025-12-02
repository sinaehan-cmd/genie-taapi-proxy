from flask import Blueprint, jsonify
from services.market_service import mvrv_run

bp = Blueprint("mvrv_routes", __name__)

@bp.route("/mvrv/run")
def mvrv_run_route():
    return jsonify(mvrv_run())

# Apps Script 구버전 호환
@bp.route("/mvrv")
def mvrv_redirect():
    return jsonify(mvrv_run())
