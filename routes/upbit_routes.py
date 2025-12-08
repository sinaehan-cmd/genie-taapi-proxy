# routes/upbit_routes.py
# Upbit API 테스트용 라우터

from flask import Blueprint, jsonify
from services.upbit_service import fetch_ticker, fetch_orderbook, fetch_market_list

upbit_bp = Blueprint("upbit_routes", __name__)

@upbit_bp.route("/test/upbit/ticker")
def test_ticker():
    """BTC 현재가 테스트"""
    res = fetch_ticker("KRW-BTC")
    return jsonify(res)

@upbit_bp.route("/test/upbit/orderbook")
def test_orderbook():
    """BTC 호가 테스트"""
    res = fetch_orderbook("KRW-BTC")
    return jsonify(res)

@upbit_bp.route("/test/upbit/markets")
def test_markets():
    """전체 마켓 조회 테스트"""
    res = fetch_market_list()
    return jsonify(res)
