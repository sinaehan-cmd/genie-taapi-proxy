from flask import Blueprint, jsonify
import datetime, os, psutil

bp = Blueprint("loop_system", __name__)

@bp.route("/system_log",methods=["GET", "POST"])
def system_log():
    """
    시스템 상태 로그 루프 – CPU, 메모리, Uptime 등 기록
    """
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory().percent

        print(f"⚙️ [SystemLog] {now} | CPU {cpu}% | MEM {mem}%")

        return jsonify({
            "timestamp": now,
            "cpu_usage": cpu,
            "memory_usage": mem,
            "status": "OK"
        })
    except Exception as e:
        print("❌ System Log Error:", e)
        return jsonify({"error": str(e)}), 500

