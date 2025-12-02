from flask import Blueprint
from loops.prediction_loop import run_prediction_loop
from loops.gti_loop import run_gti_loop

loop_bp = Blueprint("loop_routes", __name__)

@loop_bp.route("/run/prediction")
def run_prediction():
    return run_prediction_loop()

@loop_bp.route("/run/gti")
def run_gti():
    return run_gti_loop()

