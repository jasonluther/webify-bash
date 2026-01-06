# webify-bash

> **Disclaimer**: Demonstration only. Not for production use.

HTTP API for executing allowlisted shell commands. Built with FastAPI.

## Quick Start

```bash
# Create .env file
echo "BEARER_TOKEN=secret" > .env

# Run server (uses GitHub container image by default)
./run-server.py

# Or run with uvicorn directly
./run-server.py --uvicorn

# Or build and run local container
./run-server.py --local-container

# Stop container
./run-server.py stop
```

Test with curl:

```bash
curl -X POST http://localhost:8000/execute \
  -H "Authorization: Bearer secret" \
  -H "Content-Type: application/json" \
  -d '{"command": "./demo.sh", "flags": ["-n 3", "-m hello", "-u"]}'
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
{"command": "./demo.sh", "flags": ["-n 3", "-m hello"]}
```

Response:

```json
{"executed_command": "./demo.sh -n 3 -m hello", "return_code": 0, "stdout": "hello\nhello\nhello\n", "stderr": ""}
```

## Configuration

Copy `.env.example` to `.env` and set your values:

```bash
cp .env.example .env
# Edit .env and set BEARER_TOKEN
```

| Variable | Default | Description |
|----------|---------|-------------|
| `BEARER_TOKEN` | (required) | Auth token - app won't start without it |
| `PORT` | `8000` | Server port |
| `HOST` | `0.0.0.0` | Server host |
| `COMMAND_TIMEOUT` | `30` | Command timeout in seconds |
| `ALLOWED_ORIGINS` | `https://jasonluther.github.io` | CORS origins (comma-separated) |
| `CONTAINER_NAME` | `webify-bash` | Container name |
| `LOCAL_IMAGE_NAME` | `webify-bash` | Local container image name |
| `GHCR_IMAGE` | `ghcr.io/jasonluther/webify-bash:latest` | GitHub container image |
| `COMMANDS_FILE` | `commands.json` | Path to commands config |

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
- No file-reading commands (ls, cat, head, etc.)
