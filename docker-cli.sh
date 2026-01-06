#!/bin/bash
# Run CLI commands via Docker
#
# Usage: ./docker-cli.sh <command> [flags...] [args...]
#        ./docker-cli.sh ls -l /tmp
#        ./docker-cli.sh cat /etc/hostname
#
# Requires: API_URL and BEARER_TOKEN in .env or environment

set -e

IMAGE_NAME="webify-bash"

# Load from .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

API_URL="${API_URL:-http://host.docker.internal:8000}"

docker run --rm \
    -e API_URL="$API_URL" \
    -e BEARER_TOKEN="$BEARER_TOKEN" \
    "$IMAGE_NAME" \
    python cli.py "$@"
