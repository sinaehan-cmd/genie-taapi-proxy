# -*- coding: utf-8 -*-
# ======================================================
# 📊 Genie System – Final Loop Pack (render_loop 포함)
# ======================================================

from flask import Blueprint, jsonify
import requests, datetime, os

bp = Blueprint("loop_final", __name__)

# Render 서버 BASE URL
RENDER_BASE = os.getenv("RENDER_BASE_URL", "https://genie-taapi-proxy-1.onrender.com")


# ======================================================
# 📘 1) Final Briefing — 모든 루프 데이터 수집
# ======================================================
@bp.route("/final_briefing", methods=["GET", "POST"])
def final_briefing():
    """
    모든 루프 결과를 모아서 최종 브리핑 생성
    """
    try:
        print("📊 [FinalBriefing] 수집 시작")
        endpoints = ["prediction_loop", "gti_loop", "learning_loop", "system_log"]
        results = {}

        # Render 서버 루프 호출 (localhost 금지)
        for ep in endpoints:
            try:
                r = requests.get(f"{RENDER_BASE}/{ep}", timeout=10)
                results[ep] = r.json()
            except Exception as inner_e:
                results[ep] = {"error": str(inner_e)}

        summary = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": "최종 브리핑 데이터 수집 완료",
            "modules": results
        }

        print("✅ Final briefing complete.")
        return jsonify(summary)

    except Exception as e:
        print("❌ FinalBriefing Error:", e)
        return jsonify({"error": str(e)}), 500



# ======================================================
# 🚀 2) render_loop — Render가 호출하는 최종 종합 루프
# ======================================================
@bp.route("/render_loop", methods=["GET", "POST"])
def render_loop():
    """
    Render에서 호출할 전체 루프 실행 (브리핑 + 예측 + GTI + 러닝 포함)
    """
    try:
        print("\n🚀 [RenderLoop] 실행 시작 --------------------------------")

        endpoints = [
            "auto_loop",          # 시장 브리핑 루프
            "prediction_loop",    # 예측
            "gti_loop",           # GTI 계산
            "learning_loop",      # 학습 루프
            "auto_gti_loop",      # 자동 GTI
            "dominance/snapshot", # 도미넌스 30분 스냅샷
            "mvrv",               # MVRV Z-score 계산
            "reader_loop",        # 데이터 리더
        ]

        results = {}

        # 루프 순차 실행 (모든 호출 Render BASE URL로!)
        for ep in endpoints:
            try:
                print(f"👉 실행: {ep}")
                r = requests.post(f"{RENDER_BASE}/{ep}", json={}, timeout=15)
                results[ep] = r.json()
                print(f"   ✓ 완료: {ep}")
            except Exception as inner_e:
                print(f"   ✗ 실패: {ep} ({inner_e})")
                results[ep] = {"error": str(inner_e)}

        print("🔥 모든 루프 종료, FinalBriefing 생성 중...")
        fb = requests.get(f"{RENDER_BASE}/final_briefing", timeout=10).json()

        return jsonify({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "render_loop": "completed",
            "results": results,
            "final_briefing": fb
        })

    except Exception as e:
        print("💥 RenderLoop Error:", e)
        return jsonify({"error": str(e)}), 500
