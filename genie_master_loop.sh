#!/bin/bash
# ======================================================
# 🧠 Genie Master Loop – Unified Execution v3.0
# ======================================================
ACCESS_KEY="mySecretGenieKey_2025"
BASE_URL="https://genie-taapi-proxy-1.onrender.com"

while true; do
  echo "🕐 Starting full Genie loop at $(date '+%Y-%m-%d %H:%M:%S')"

  curl -s -X POST $BASE_URL/auto_loop \
    -H "Content-Type: application/json" \
    -d "{\"access_key\":\"$ACCESS_KEY\"}"
  sleep 5

  curl -s -X POST $BASE_URL/prediction_loop \
    -H "Content-Type: application/json" \
    -d "{\"access_key\":\"$ACCESS_KEY\"}"
  sleep 5

  curl -s -X POST $BASE_URL/gti_loop \
    -H "Content-Type: application/json" \
    -d "{\"access_key\":\"$ACCESS_KEY\"}"
  sleep 5

  curl -s -X POST $BASE_URL/learning_loop \
    -H "Content-Type: application/json" \
    -d "{\"access_key\":\"$ACCESS_KEY\"}"
  sleep 5

  curl -s -X POST $BASE_URL/system_log \
    -H "Content-Type: application/json" \
    -d "{\"access_key\":\"$ACCESS_KEY\",\"module\":\"GENIE_MASTER_LOOP\",\"status\":\"✅OK\",\"runtime\":\"AUTO\"}"

  echo "✅ Loop completed. Sleeping for 1 hour..."
  sleep 3600
done
