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

## Web UI

<https://jasonluther.github.io/webify-bash/>

To enable for your fork: Settings → Pages → Branch: `main`, folder: `/docs`

## API

```text
POST /execute   - Execute a command
GET  /commands  - List allowed commands
GET  /docs      - Interactive API docs
```

Request:

```json
{"command": "head", "flags": ["-n 5"], "args": ["/etc/hosts"]}
```

Response:

```json
{"executed_command": "head -n 5 /etc/hosts", "return_code": 0, "stdout": "...", "stderr": ""}
```

## Configuration

| Variable | Description |
|----------|-------------|
| `BEARER_TOKEN` | Auth token (required) |

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
