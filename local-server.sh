#!/bin/bash
# Start the local FastAPI server
#
# Usage: ./local-server.sh
#        HOST=127.0.0.1 PORT=3000 ./local-server.sh

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

echo "Starting server at http://$HOST:$PORT"
echo "API docs at http://$HOST:$PORT/docs"
echo ""

uvicorn app:app --host "$HOST" --port "$PORT"
