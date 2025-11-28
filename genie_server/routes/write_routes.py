# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
from genie_server.utils.google_sheets import write_row
from genie_server.config import GENIE_ACCESS_KEY

bp = Blueprint("write_routes", __name__)

@bp.route("/write", methods=["POST"])
def write_data():
    try:
        data = request.get_json(force=True)

        if data.get("access_key") != GENIE_ACCESS_KEY:
            return jsonify({"error": "Invalid access key"}), 403

        sheet_name = data.get("sheet_name")
        values = data.get("values", [])

        write_row(sheet_name, values)

        print(f"✅ GoogleSheet WRITE → {sheet_name}: {values}")

        return jsonify({
            "result": "success",
            "sheet": sheet_name,
            "values": values
        })

    except Exception as e:
        print("❌ write 오류:", e)
        return jsonify({"error": str(e)}), 500
