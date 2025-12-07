# routes/loop_routes.py
# Genie Server v2025.12 — Unified Loop Router (Stable)

from flask import Blueprint, jsonify

# 개별 루프
from loops.reader_loop import run_reader_loop
from loops.prediction_loop import run_prediction_loop
from loops.gti_loop import run_gti_loop
from loops.learning_loop import run_learning_loop
from loops.auto_gti_loop import run_auto_gti_loop
from loops.system_log_loop import run_system_log_loop

# 전체 자동 루프
from loops.auto_loop import run_auto_loop

loop_bp = Blueprint("loop_routes", __name__)

# -----------------------------
# 개별 루프 실행
# -----------------------------
@loop_bp.route("/run/reader")
def run_reader():
    return jsonify(run_reader_loop())

@loop_bp.route("/run/prediction")
def run_prediction():
    return jsonify(run_prediction_loop())

@loop_bp.route("/run/gti")
def run_gti():
    return jsonify(run_gti_loop())

@loop_bp.route("/run/learning")
def run_learning():
    return jsonify(run_learning_loop())

@loop_bp.route("/run/system_log")
def run_system_log():
    return jsonify(run_system_log_loop())

@loop_bp.route("/run/auto_gti")
def run_auto_gti():
    return jsonify(run_auto_gti_loop())


# -----------------------------
# ⭐ 전체 자동 루프 (핵심)
# -----------------------------
@loop_bp.route("/run/auto")
def run_auto():
    """
    전체 자동 루프 구성:
      1) Reader
      2) Prediction
      3) GTI
      4) Learning
      5) AutoGTI
      6) SystemLog
    """
    return jsonify(run_auto_loop())
