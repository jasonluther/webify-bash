#!/bin/bash
# Start the local FastAPI server
#
# Usage: ./local-server.sh [--docker]
#        HOST=127.0.0.1 PORT=3000 ./local-server.sh
#
# Options:
#   --docker    Build and run in Docker container

set -e

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
IMAGE_NAME="webify-bash"

if [ "$1" = "--docker" ]; then
    echo "Building Docker image..."
    docker build -t "$IMAGE_NAME" .

    echo ""
    echo "Starting container at http://localhost:$PORT"
    echo "API docs at http://localhost:$PORT/docs"
    echo ""

    # Load BEARER_TOKEN from .env if it exists
    if [ -f .env ]; then
        export $(grep -v '^#' .env | xargs)
    fi

    docker run --rm -p "$PORT:8000" -e BEARER_TOKEN="$BEARER_TOKEN" "$IMAGE_NAME"
else
    echo "Starting server at http://$HOST:$PORT"
    echo "API docs at http://$HOST:$PORT/docs"
    echo ""

    uvicorn app:app --host "$HOST" --port "$PORT"
fi
