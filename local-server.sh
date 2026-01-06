#!/bin/bash
set -e

PORT="${PORT:-8000}"
IMAGE_NAME="webify-bash"

if [ "$1" = "--container" ]; then
    if command -v podman &>/dev/null; then
        CMD="podman"
    elif command -v docker &>/dev/null; then
        CMD="docker"
    else
        echo "Error: podman or docker required" >&2
        exit 1
    fi
    [ -z "$BEARER_TOKEN" ] && echo "Error: BEARER_TOKEN not set" >&2 && exit 1

    echo "Building and starting container at http://localhost:$PORT"
    $CMD build -t "$IMAGE_NAME" .
    $CMD run --rm -p "$PORT:8000" -e BEARER_TOKEN="$BEARER_TOKEN" "$IMAGE_NAME"
else
    echo "Starting server at http://localhost:$PORT"
    uvicorn app:app --host 0.0.0.0 --port "$PORT"
fi
