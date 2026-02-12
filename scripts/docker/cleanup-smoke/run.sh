#!/usr/bin/env bash
set -euo pipefail

cd /repo

export NEMO_STATE_DIR="/tmp/nemo-test"
export NEMO_CONFIG_PATH="${NEMO_STATE_DIR}/nemo.json"

echo "==> Build"
pnpm build

echo "==> Seed state"
mkdir -p "${NEMO_STATE_DIR}/credentials"
mkdir -p "${NEMO_STATE_DIR}/agents/main/sessions"
echo '{}' >"${NEMO_CONFIG_PATH}"
echo 'creds' >"${NEMO_STATE_DIR}/credentials/marker.txt"
echo 'session' >"${NEMO_STATE_DIR}/agents/main/sessions/sessions.json"

echo "==> Reset (config+creds+sessions)"
pnpm nemo reset --scope config+creds+sessions --yes --non-interactive

test ! -f "${NEMO_CONFIG_PATH}"
test ! -d "${NEMO_STATE_DIR}/credentials"
test ! -d "${NEMO_STATE_DIR}/agents/main/sessions"

echo "==> Recreate minimal config"
mkdir -p "${NEMO_STATE_DIR}/credentials"
echo '{}' >"${NEMO_CONFIG_PATH}"

echo "==> Uninstall (state only)"
pnpm nemo uninstall --state --yes --non-interactive

test ! -d "${NEMO_STATE_DIR}"

echo "OK"
