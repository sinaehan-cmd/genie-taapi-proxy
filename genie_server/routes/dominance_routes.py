from flask import Blueprint, jsonify
from genie_server.utils.dominance_fetcher import (
    get_current_dominance,
    get_avg,
    get_dominance_packet
)

bp = Blueprint("dominance", __name__, url_prefix="/dominance")


@bp.route("/now")
def dominance_now():
    """단일 현재 도미넌스 조회"""
    v = get_current_dominance()
    return jsonify({
        "dominance": v if v is not None else "값없음"
    })


@bp.route("/avg/<int:hours>")
def dominance_avg(hours):
    """4h 또는 24h 평균"""
    v = get_avg(hours)
    return jsonify({
        "avg": v if v is not None else "값없음"
    })


@bp.route("/packet")
def dominance_packet():
    """
    Apps Script에서 바로 사용 가능한 모든 도미넌스 패킷
    {
      "dominance": 56.23,
      "dominance_4h": 55.88,
      "dominance_1d": 54.91
    }
    """
    data = get_dominance_packet()
    return jsonify(data)
