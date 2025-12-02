# routes/dominance_routes.py

from flask import Blueprint
from .dominance_core import dominance_snapshot   # 최신 Dominance 함수

bp = Blueprint("dominance_routes", __name__)

# Apps Script 구버전 호환
@bp.route("/dominance/packet", methods=["GET", "POST"])
def dominance_redirect():
    return dominance_snapshot()
