# routes/mvrv_routes.py

from flask import Blueprint
from .mvrv_core import mvrv_run    # 네가 만든 실제 MVRV 계산 함수

bp = Blueprint("mvrv_routes", __name__)

# Apps Script 구버전 호환(필수)
@bp.route("/mvrv", methods=["GET", "POST"])
def mvrv_redirect():
    return mvrv_run()
