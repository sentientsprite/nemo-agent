#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_NAME="${NEMO_IMAGE:-${NEMO_IMAGE:-nemo:local}}"
CONFIG_DIR="${NEMO_CONFIG_DIR:-${NEMO_CONFIG_DIR:-$HOME/.nemo}}"
WORKSPACE_DIR="${NEMO_WORKSPACE_DIR:-${NEMO_WORKSPACE_DIR:-$HOME/.nemo/workspace}}"
PROFILE_FILE="${NEMO_PROFILE_FILE:-${NEMO_PROFILE_FILE:-$HOME/.profile}}"

PROFILE_MOUNT=()
if [[ -f "$PROFILE_FILE" ]]; then
  PROFILE_MOUNT=(-v "$PROFILE_FILE":/home/node/.profile:ro)
fi

echo "==> Build image: $IMAGE_NAME"
docker build -t "$IMAGE_NAME" -f "$ROOT_DIR/Dockerfile" "$ROOT_DIR"

echo "==> Run gateway live model tests (profile keys)"
docker run --rm -t \
  --entrypoint bash \
  -e COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
  -e HOME=/home/node \
  -e NODE_OPTIONS=--disable-warning=ExperimentalWarning \
  -e NEMO_LIVE_TEST=1 \
  -e NEMO_LIVE_GATEWAY_MODELS="${NEMO_LIVE_GATEWAY_MODELS:-${NEMO_LIVE_GATEWAY_MODELS:-all}}" \
  -e NEMO_LIVE_GATEWAY_PROVIDERS="${NEMO_LIVE_GATEWAY_PROVIDERS:-${NEMO_LIVE_GATEWAY_PROVIDERS:-}}" \
  -e NEMO_LIVE_GATEWAY_MODEL_TIMEOUT_MS="${NEMO_LIVE_GATEWAY_MODEL_TIMEOUT_MS:-${NEMO_LIVE_GATEWAY_MODEL_TIMEOUT_MS:-}}" \
  -v "$CONFIG_DIR":/home/node/.nemo \
  -v "$WORKSPACE_DIR":/home/node/.nemo/workspace \
  "${PROFILE_MOUNT[@]}" \
  "$IMAGE_NAME" \
  -lc "set -euo pipefail; [ -f \"$HOME/.profile\" ] && source \"$HOME/.profile\" || true; cd /app && pnpm test:live"
