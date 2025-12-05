# routes/loop_fix_routes.py
# Genie Loop 복원 전용 — V5 Collector와 완전 분리된 안전판

from flask import Blueprint, jsonify
from loops.prediction_loop import run_prediction_loop
from loops.gti_loop import run_gti_loop
from loops.learning_loop import run_learning_loop
from loops.auto_loop import run_auto_feedback_loop
from loops.auto_gti_loop import run_auto_gti_loop
from loops.system_log_loop import run_system_log_loop
from loops.reader_loop import run_reader_loop   # (있을 경우)

loop_fix_bp = Blueprint("loop_fix_routes", __name__)


# --------------------------------------------------------
# 🔵 1) /loop/auto → Auto Feedback Loop
# --------------------------------------------------------
@loop_fix_bp.route("/loop/auto", methods=["POST", "GET"])
def loop_auto():
    return jsonify(run_auto_feedback_loop())


# --------------------------------------------------------
# 🔵 2) /loop/prediction → Prediction Loop
# (기존 /run/prediction API도 유지됨 — 충돌 없음)
# --------------------------------------------------------
@loop_fix_bp.route("/loop/prediction", methods=["POST", "GET"])
def loop_prediction():
    return jsonify(run_prediction_loop())


# --------------------------------------------------------
# 🔵 3) /loop/gti → GTI Loop
# --------------------------------------------------------
@loop_fix_bp.route("/loop/gti", methods=["POST", "GET"])
def loop_gti():
    return jsonify(run_gti_loop())


# --------------------------------------------------------
# 🔵 4) /loop/learning → Learning Loop
# --------------------------------------------------------
@loop_fix_bp.route("/loop/learning", methods=["POST", "GET"])
def loop_learning():
    return jsonify(run_learning_loop())


# --------------------------------------------------------
# 🔵 5) /loop/auto_gti → Auto GTI Loop
# --------------------------------------------------------
@loop_fix_bp.route("/loop/auto_gti", methods=["POST", "GET"])
def loop_auto_gti():
    return jsonify(run_auto_gti_loop())


# --------------------------------------------------------
# 🔵 6) /dominance/snapshot → Snapshot Alias
# (기존 /dominance/packet 은 Collector가 사용 → 유지)
# --------------------------------------------------------
@loop_fix_bp.route("/dominance/snapshot", methods=["POST", "GET"])
def dominance_snapshot():
    from services.dominance_service import get_dominance_packet
    return jsonify(get_dominance_packet())


# --------------------------------------------------------
# 🔵 7) /mvrv/run → MVRV 계산 루프용 엔드포인트
# (기존 /mvrv 은 Collector API → 유지)
# --------------------------------------------------------
@loop_fix_bp.route("/mvrv/run", methods=["POST", "GET"])
def mvrv_run():
    from services.mvrv_service import calc_mvrv_z
    from services.price_service import get_btc_price

    price = get_btc_price()
    if price is None:
        return jsonify({"error": "price fetch failed"}), 500

    z = calc_mvrv_z(price)
    return jsonify({"price": price, "MVRV_Z": z})


# --------------------------------------------------------
# 🔵 8) /reader/run → Reader Loop
# (없을 경우 자동 무시)
# --------------------------------------------------------
try:
    @loop_fix_bp.route("/reader/run", methods=["POST", "GET"])
    def reader_run():
        return jsonify(run_reader_loop())
except:
    pass


# --------------------------------------------------------
# 🔵 9) /system/log → System Log Loop
# --------------------------------------------------------
@loop_fix_bp.route("/system/log", methods=["POST", "GET"])
def system_log():
    return jsonify(run_system_log_loop())
