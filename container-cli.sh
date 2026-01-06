#!/bin/bash
set -e

IMAGE_NAME="webify-bash"

[ -f .env ] && export $(grep -v '^#' .env | xargs)

if command -v podman &>/dev/null; then
    CMD="podman"
    NETWORK="--network host"
    API_URL="${API_URL:-http://localhost:8000}"
elif command -v docker &>/dev/null; then
    CMD="docker"
    NETWORK=""
    API_URL="${API_URL:-http://host.docker.internal:8000}"
else
    echo "Error: podman or docker required" >&2
    exit 1
fi

$CMD run --rm $NETWORK -e API_URL="$API_URL" -e BEARER_TOKEN="$BEARER_TOKEN" "$IMAGE_NAME" python cli.py "$@"
