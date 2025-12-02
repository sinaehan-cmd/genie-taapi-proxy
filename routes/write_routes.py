from flask import Blueprint, request, jsonify
from services.google_sheets import append_row
import datetime

write_bp = Blueprint("write_routes", __name__)

@write_bp.route("/write", methods=["POST"])
def write():
    body = request.json
    sheet = body["sheet"]
    values = body["values"]
    append_row(sheet, values)
    return jsonify({"status": "ok"})

