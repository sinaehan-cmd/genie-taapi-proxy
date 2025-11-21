from flask import Blueprint, jsonify, request
from genie_server.utils.google_sheets import get_sheets_service
from genie_server.config import SHEET_ID, GENIE_ACCESS_KEY

bp = Blueprint("write_routes", __name__)

@bp.route("/write", methods=["POST"])
def write_data():
    try:
        data = request.get_json(force=True)
        if data.get("access_key") != GENIE_ACCESS_KEY:
            return jsonify({"error": "Invalid access key"}), 403
        sheet_name = data.get("sheet_name")
        values = [data.get("values", [])]
        service = get_sheets_service(write=True)
        service.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range=sheet_name,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": values},
        ).execute()
        print(f"✅ Data written to {sheet_name}: {values}")
        return jsonify({"result": "success", "sheet_name": sheet_name})
    except Exception as e:
        print("❌ write 오류:", e)
        return jsonify({"error": str(e)}), 500


