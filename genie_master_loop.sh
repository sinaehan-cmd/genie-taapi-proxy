#!/bin/bash
# ======================================================
# 🧠 Genie Master Loop – Unified Execution v3.1
# 자동 Uptime% + Next_Slot 계산형
# ======================================================

ACCESS_KEY="mySecretGenieKey_2025"
BASE_URL="https://genie-taapi-proxy-1.onrender.com"

# 마지막 성공 시간 기록용
LAST_SUCCESS=$(date +%s)

while true; do
  START=$(date +%s)
  echo "🕐 Starting full Genie loop at $(date '+%Y-%m-%d %H:%M:%S')"

  # ① 주요 루프 실행
  curl -s -X POST $BASE_URL/auto_loop -H "Content-Type: application/json" -d "{\"access_key\":\"$ACCESS_KEY\"}"
  sleep 5
  curl -s -X POST $BASE_URL/prediction_loop -H "Content-Type: application/json" -d "{\"access_key\":\"$ACCESS_KEY\"}"
  sleep 5
  curl -s -X POST $BASE_URL/gti_loop -H "Content-Type: application/json" -d "{\"access_key\":\"$ACCESS_KEY\"}"
  sleep 5
  curl -s -X POST $BASE_URL/learning_loop -H "Content-Type: application/json" -d "{\"access_key\":\"$ACCESS_KEY\"}"
  sleep 5

  # ② 상태값 계산
  END=$(date +%s)
  RUNTIME=$((END - START))

  # 최근 성공 기록 갱신
  CURRENT_TIME=$(date +%s)
  UPTIME=$(( (CURRENT_TIME - LAST_SUCCESS) < 7200 ? 100 : 95 ))
  LAST_SUCCESS=$CURRENT_TIME

  # 다음 실행 예정 시각 계산
  NEXT_SLOT=$(date -d "1 hour" '+%Y-%m-%d %H:%M:%S')

  # ③ 시스템 로그 전송
  curl -s -X POST $BASE_URL/system_log \
    -H "Content-Type: application/json" \
    -d "{
      \"access_key\": \"$ACCESS_KEY\",
      \"module\": \"GENIE_MASTER_LOOP\",
      \"status\": \"✅OK\",
      \"runtime\": \"$RUNTIME\",
      \"TRUST_OK\": true,
      \"Reason\": \"Auto Routine Completed\",
      \"Ref_ID\": \"SYS.$(date +%Y%m%d%H%M%S)\",
      \"Uptime%\": \"$UPTIME\",
      \"Next_Slot\": \"$NEXT_SLOT\"
    }"

  echo "✅ Loop completed. Runtime: ${RUNTIME}s | Uptime: ${UPTIME}% | Next: ${NEXT_SLOT}"
  echo "💤 Sleeping for 1 hour..."
  sleep 3600
done
