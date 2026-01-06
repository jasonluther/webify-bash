#!/bin/bash
# Start the local FastAPI server
#
# Usage: ./local-server.sh [--container]
#        HOST=127.0.0.1 PORT=3000 ./local-server.sh
#
# Options:
#   --container    Build and run in container (uses podman, falls back to docker)

set -e

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
IMAGE_NAME="webify-bash"

# Prefer podman, fall back to docker
if command -v podman &>/dev/null; then
    CONTAINER_CMD="podman"
elif command -v docker &>/dev/null; then
    CONTAINER_CMD="docker"
else
    CONTAINER_CMD=""
fi

if [ "$1" = "--container" ] || [ "$1" = "--docker" ]; then
    if [ -z "$CONTAINER_CMD" ]; then
        echo "Error: podman or docker required" >&2
        exit 1
    fi

    echo "Building image with $CONTAINER_CMD..."
    $CONTAINER_CMD build -t "$IMAGE_NAME" .

    echo ""
    echo "Starting container at http://localhost:$PORT"
    echo "API docs at http://localhost:$PORT/docs"
    echo ""

    # Load BEARER_TOKEN from .env if it exists
    if [ -f .env ]; then
        export $(grep -v '^#' .env | xargs)
    fi

    $CONTAINER_CMD run --rm -p "$PORT:8000" -e BEARER_TOKEN="$BEARER_TOKEN" "$IMAGE_NAME"
else
    echo "Starting server at http://$HOST:$PORT"
    echo "API docs at http://$HOST:$PORT/docs"
    echo ""

    uvicorn app:app --host "$HOST" --port "$PORT"
fi
