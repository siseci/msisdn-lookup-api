#!/usr/bin/env bash
# MSISDN Lookup API başlatma scripti
# Kullanım: ./start.sh [workers]
set -e

WORKERS=${1:-1}
PORT=8090

echo "MSISDN Lookup API başlatılıyor → port $PORT, workers=$WORKERS"

python3 -m uvicorn main:app \
  --host 0.0.0.0 \
  --port $PORT \
  --workers $WORKERS \
  --loop asyncio \
  --log-level info
