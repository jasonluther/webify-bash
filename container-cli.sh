#!/bin/bash
# Run CLI commands via container (podman or docker)
#
# Usage: ./container-cli.sh <command> [flags...] [args...]
#        ./container-cli.sh ls -l /tmp
#        ./container-cli.sh uname -a
#
# Requires: API_URL and BEARER_TOKEN in .env or environment

set -e

IMAGE_NAME="webify-bash"

# Load from .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Prefer podman, fall back to docker
if command -v podman &>/dev/null; then
    CONTAINER_CMD="podman"
    # Podman uses host network
    NETWORK_OPTS="--network host"
    API_URL="${API_URL:-http://localhost:8000}"
elif command -v docker &>/dev/null; then
    CONTAINER_CMD="docker"
    NETWORK_OPTS=""
    API_URL="${API_URL:-http://host.docker.internal:8000}"
else
    echo "Error: podman or docker required" >&2
    exit 1
fi

$CONTAINER_CMD run --rm $NETWORK_OPTS \
    -e API_URL="$API_URL" \
    -e BEARER_TOKEN="$BEARER_TOKEN" \
    "$IMAGE_NAME" \
    python cli.py "$@"
