#!/bin/bash
# CLI tool to invoke shell commands via the API

set -e

# Load config from .env if present
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

API_URL="${API_URL:-http://localhost:8000}"
TOKEN="${BEARER_TOKEN:-}"

usage() {
    echo "Usage: $0 <command> [flags...] [args...]"
    echo ""
    echo "Examples:"
    echo "  $0 ls -l /tmp"
    echo "  $0 uname -a"
    echo ""
    echo "Environment variables:"
    echo "  API_URL      - API base URL (default: http://localhost:8000)"
    echo "  BEARER_TOKEN - Authentication token (required)"
    exit 1
}

if [ -z "$TOKEN" ]; then
    echo "Error: BEARER_TOKEN not set" >&2
    exit 1
fi

if [ $# -lt 1 ]; then
    # List available commands
    RESPONSE=$(curl -s "$API_URL/commands" -H "Authorization: Bearer $TOKEN")
    echo "Available commands:"
    echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for cmd, config in sorted(data.items()):
    flags = ' '.join(config['flags']) if config['flags'] else '(none)'
    bare = 'yes' if config['bare_arg'] else 'no'
    print(f'  {cmd}: flags=[{flags}] bare_args={bare}')
"
    exit 0
fi

CMD="$1"
shift

# Parse flags (start with -) and args (don't start with -)
FLAGS=()
ARGS=()

while [ $# -gt 0 ]; do
    if [[ "$1" == -* ]]; then
        FLAGS+=("$1")
    else
        ARGS+=("$1")
    fi
    shift
done

# Build JSON payload
build_json() {
    local json="{\"command\": \"$CMD\""

    if [ ${#FLAGS[@]} -gt 0 ]; then
        json+=", \"flags\": ["
        local first=true
        for flag in "${FLAGS[@]}"; do
            if $first; then
                first=false
            else
                json+=", "
            fi
            json+="\"$flag\""
        done
        json+="]"
    fi

    if [ ${#ARGS[@]} -gt 0 ]; then
        json+=", \"args\": ["
        local first=true
        for arg in "${ARGS[@]}"; do
            if $first; then
                first=false
            else
                json+=", "
            fi
            # Escape quotes in args
            escaped=$(echo "$arg" | sed 's/"/\\"/g')
            json+="\"$escaped\""
        done
        json+="]"
    fi

    json+="}"
    echo "$json"
}

PAYLOAD=$(build_json)

# Make the API call
RESPONSE=$(curl -s -X POST "$API_URL/execute" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

# Parse JSON response
RETURN_CODE=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('return_code', 1))" 2>/dev/null || echo "1")
EXECUTED=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('executed_command', ''))" 2>/dev/null || echo "")
STDOUT=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('stdout', ''), end='')" 2>/dev/null || echo "")
STDERR=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('stderr', ''), end='')" 2>/dev/null || echo "")

# Check for API error
if echo "$RESPONSE" | grep -q '"detail"'; then
    ERROR=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('detail', 'Unknown error'))" 2>/dev/null)
    echo "Error: $ERROR" >&2
    exit 1
fi

# Output like the real command (command substitution strips trailing newlines, so add one back)
[ -n "$STDOUT" ] && echo "$STDOUT"
[ -n "$STDERR" ] && echo "$STDERR" >&2

exit "$RETURN_CODE"
