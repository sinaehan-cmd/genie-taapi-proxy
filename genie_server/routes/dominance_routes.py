from flask import Blueprint, request, jsonify
from genie_server.utils.dominance_fetcher import get_dominance

bp = Blueprint("dominance_routes", __name__)

@bp.route("/dominance")
def dominance_api():
    tf = request.args.get("tf", "1h")
    data = get_dominance(tf)
    return jsonify(data)
