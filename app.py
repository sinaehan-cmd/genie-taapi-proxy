from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# === TAAPI.io API 설정 ===
TAAPI_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjkwNGI5MzU4MDZmZjE2NTFlOGM1YTQ5IiwiaWF0IjoxNzYxOTIxMTIyLCJleHAiOjMzMjY2Mzg1MTIyfQ.1tCjlog-xrsmLI9zhGx6feGNaaojrMkz5HM8vcuDH8c"
BASE_URL = "https://api.taapi.io"

@app.route('/')
def home():
    return jsonify({"status": "Genie TAAPI Proxy Active ✅"})

@app.route('/indicator', methods=['GET'])
def get_indicator():
    symbol = request.args.get('symbol', 'BTC/USDT')
    exchange = request.args.get('exchange', 'binance')
    indicator = request.args.get('indicator', 'rsi')
    interval = request.args.get('interval', '1h')

    try:
        url = f"{BASE_URL}/{indicator}?secret={TAAPI_KEY}&exchange={exchange}&symbol={symbol}&interval={interval}"
        response = requests.get(url)
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
