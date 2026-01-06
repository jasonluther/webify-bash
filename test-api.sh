#!/bin/bash
# Test script for webify-bash API
# Usage: ./test-api.sh [URL] [TOKEN]
#   URL defaults to http://localhost:8000
#   TOKEN defaults to BEARER_TOKEN from .env

set -euo pipefail

URL="${1:-http://localhost:8000}"
TOKEN="${2:-${BEARER_TOKEN:-}}"

if [ -z "$TOKEN" ]; then
    if [ -f .env ]; then
        TOKEN=$(grep BEARER_TOKEN .env | cut -d= -f2)
    fi
fi

if [ -z "$TOKEN" ]; then
    echo "Error: No token provided. Set BEARER_TOKEN or pass as argument."
    exit 1
fi

echo "Testing API at: $URL"
echo "================================"

# Test health endpoint (no auth required)
echo -e "\n[1] GET /health"
curl -sf "$URL/health" && echo " OK" || echo " FAILED"

# Test commands endpoint
echo -e "\n[2] GET /commands"
RESULT=$(curl -sf "$URL/commands" -H "Authorization: Bearer $TOKEN")
if echo "$RESULT" | grep -q "demo.sh"; then
    echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Found {len(d)} commands: {list(d.keys())}')"
else
    echo "  FAILED: $RESULT"
fi

# Test echo command
echo -e "\n[3] POST /execute - echo"
RESULT=$(curl -sf -X POST "$URL/execute" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"command": "echo", "args": ["hello world"]}')
if echo "$RESULT" | grep -q '"return_code":0'; then
    echo "  OK: $(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['stdout'].strip())")"
else
    echo "  FAILED: $RESULT"
fi

# Test demo.sh with short flags
echo -e "\n[4] POST /execute - demo.sh -n 2 -m test"
RESULT=$(curl -sf -X POST "$URL/execute" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"command": "./demo.sh", "flags": ["-n 2", "-m test"]}')
if echo "$RESULT" | grep -q '"return_code":0'; then
    echo "  OK: $(echo "$RESULT" | python3 -c "import sys,json; print(repr(json.load(sys.stdin)['stdout']))")"
else
    echo "  FAILED: $RESULT"
fi

# Test demo.sh with long flags
echo -e "\n[5] POST /execute - demo.sh --count 2 --message hello"
RESULT=$(curl -sf -X POST "$URL/execute" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"command": "./demo.sh", "flags": ["--count 2", "--message hello"]}')
if echo "$RESULT" | grep -q '"return_code":0'; then
    echo "  OK: $(echo "$RESULT" | python3 -c "import sys,json; print(repr(json.load(sys.stdin)['stdout']))")"
else
    echo "  FAILED: $RESULT"
fi

# Test demo.sh with uppercase flag
echo -e "\n[6] POST /execute - demo.sh -n 1 -m hi -u"
RESULT=$(curl -sf -X POST "$URL/execute" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"command": "./demo.sh", "flags": ["-n 1", "-m hi", "-u"]}')
if echo "$RESULT" | grep -q '"return_code":0'; then
    echo "  OK: $(echo "$RESULT" | python3 -c "import sys,json; print(repr(json.load(sys.stdin)['stdout']))")"
else
    echo "  FAILED: $RESULT"
fi

# Test invalid token
echo -e "\n[7] POST /execute - invalid token (expect 401)"
RESULT=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$URL/execute" \
    -H "Authorization: Bearer wrong-token" \
    -H "Content-Type: application/json" \
    -d '{"command": "echo", "args": ["test"]}')
if [ "$RESULT" = "401" ]; then
    echo "  OK: Got 401 Unauthorized"
else
    echo "  FAILED: Expected 401, got $RESULT"
fi

# Test invalid command
echo -e "\n[8] POST /execute - invalid command (expect 400)"
RESULT=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$URL/execute" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"command": "rm", "args": ["-rf", "/"]}')
if [ "$RESULT" = "400" ]; then
    echo "  OK: Got 400 Bad Request"
else
    echo "  FAILED: Expected 400, got $RESULT"
fi

# Test invalid flag
echo -e "\n[9] POST /execute - invalid flag (expect 400)"
RESULT=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$URL/execute" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"command": "echo", "args": [], "flags": ["--delete"]}')
if [ "$RESULT" = "400" ]; then
    echo "  OK: Got 400 Bad Request"
else
    echo "  FAILED: Expected 400, got $RESULT"
fi

# Test date command
echo -e "\n[10] POST /execute - date -u"
RESULT=$(curl -sf -X POST "$URL/execute" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"command": "date", "flags": ["-u"]}')
if echo "$RESULT" | grep -q '"return_code":0'; then
    echo "  OK: $(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['stdout'].strip())")"
else
    echo "  FAILED: $RESULT"
fi

echo -e "\n================================"
echo "All tests completed!"
