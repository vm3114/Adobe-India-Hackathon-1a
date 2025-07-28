#!/bin/sh

echo "[•] Starting LLM Sherpa server..." &
/app/run.sh &

echo "[•] Waiting for LLM Sherpa to be ready..."
until curl --silent --fail http://localhost:5001/ > /dev/null 2>&1; do
  sleep 1
done

echo "[✓] LLM Sherpa is up. Running extract_headings.py"
python3 extract_headings.py
