#!/usr/bin/env bash
#
# wait_for_service.sh — Wait for an HTTP endpoint to become healthy.
# Used in Jenkins pipelines before running integration/smoke tests.
#
# Usage: ./wait_for_service.sh <url> [max_retries] [interval_seconds]
#

set -euo pipefail

URL="${1:?Usage: wait_for_service.sh <url> [max_retries] [interval]}"
MAX_RETRIES="${2:-30}"
INTERVAL="${3:-2}"

echo "Waiting for ${URL} to become healthy..."
echo "  Max retries: ${MAX_RETRIES}, Interval: ${INTERVAL}s"

for i in $(seq 1 "${MAX_RETRIES}"); do
    HTTP_CODE=$(curl -sf -o /dev/null -w '%{http_code}' "${URL}" 2>/dev/null || echo "000")

    if [ "${HTTP_CODE}" = "200" ]; then
        echo "Service is healthy after ${i} attempt(s)."
        exit 0
    fi

    echo "  Attempt ${i}/${MAX_RETRIES} — HTTP ${HTTP_CODE}, retrying in ${INTERVAL}s..."
    sleep "${INTERVAL}"
done

echo "ERROR: Service at ${URL} did not become healthy after ${MAX_RETRIES} attempts."
exit 1
