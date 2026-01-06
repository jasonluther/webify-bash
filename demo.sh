#!/bin/bash
# Demo script that safely demonstrates flag values

MAX_COUNT=10
MAX_MESSAGE_LEN=100

while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--count)
            COUNT="$2"
            shift 2
            ;;
        -m|--message)
            MESSAGE="$2"
            shift 2
            ;;
        -u|--uppercase)
            UPPERCASE=1
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Validate count
COUNT="${COUNT:-1}"
if ! [[ "$COUNT" =~ ^[0-9]+$ ]] || [[ "$COUNT" -lt 1 ]] || [[ "$COUNT" -gt "$MAX_COUNT" ]]; then
    echo "Error: count must be 1-$MAX_COUNT" >&2
    exit 1
fi

# Validate message length
MESSAGE="${MESSAGE:-Hello}"
if [[ "${#MESSAGE}" -gt "$MAX_MESSAGE_LEN" ]]; then
    echo "Error: message must be <= $MAX_MESSAGE_LEN characters" >&2
    exit 1
fi

OUTPUT="$MESSAGE"

if [[ -n "$UPPERCASE" ]]; then
    OUTPUT=$(echo "$OUTPUT" | tr '[:lower:]' '[:upper:]')
fi

for ((i=1; i<=COUNT; i++)); do
    echo "$OUTPUT"
done
