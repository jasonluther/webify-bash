# webify-bash

> **Disclaimer**: Demonstration only. Not for production use.

HTTP API for executing allowlisted shell commands. Built with FastAPI.

## Quick Start

```bash
# Run with container
podman run -p 8000:8000 -e BEARER_TOKEN=secret ghcr.io/jasonluther/webify-bash

# Test
curl -X POST http://localhost:8000/execute \
  -H "Authorization: Bearer secret" \
  -H "Content-Type: application/json" \
  -d '{"command": "uname", "flags": ["-a"]}'
```

## CLI

```bash
export BEARER_TOKEN=secret
./cli.py              # list commands
./cli.py ls -l /tmp   # execute command
```

## Web UI

https://jasonluther.github.io/webify-bash/

To enable for your fork: Settings → Pages → Branch: `main`, folder: `/docs`

## API

```
POST /execute   - Execute a command
GET  /commands  - List allowed commands
GET  /docs      - Interactive API docs
```

Request:
```json
{"command": "ls", "flags": ["-l"], "args": ["/tmp"]}
```

Response:
```json
{"executed_command": "ls -l /tmp", "return_code": 0, "stdout": "...", "stderr": ""}
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `BEARER_TOKEN` | Auth token (required) | - |
| `API_URL` | API URL for CLI | `http://localhost:8000` |

## Adding Commands

Edit `commands.json`:

```json
{
  "mycommand": {"flags": ["-a", "-b"], "bare_arg": true}
}
```

## Deploy

**Railway**: Connect repo → set `BEARER_TOKEN` env var → auto-deploys on push

## Security

- Commands executed as list (no shell injection)
- Allowlist-only commands and flags
- 30 second timeout
- Bearer token required
