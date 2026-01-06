# webify-bash

A simple HTTP API for executing whitelisted shell commands safely. Built with FastAPI.

## Features

- Whitelist-based command execution (only allowed commands can run)
- Flag validation per command
- Bearer token authentication
- JSON responses with stdout, stderr, and exit code
- Container support (podman/docker)
- GitHub Actions CI with multi-platform images (amd64/arm64)

## Allowed Commands

| Command | Flags | Args |
|---------|-------|------|
| `echo` | `-n`, `-e` | yes |
| `ls` | `-l`, `-a`, `-la`, `-lh`, `-alh`, `-1`, `-R` | yes |
| `uname` | `-a`, `-s`, `-n`, `-r`, `-v`, `-m`, `-p`, `-o` | no |
| `whoami` | none | no |

## Quick Start

### Using the container image

```bash
# Pull the image
podman pull ghcr.io/jasonluther/webify-bash:latest

# Run the server
podman run -p 8000:8000 -e BEARER_TOKEN=secret ghcr.io/jasonluther/webify-bash

# Test it
curl -X POST http://localhost:8000/execute \
  -H "Authorization: Bearer secret" \
  -H "Content-Type: application/json" \
  -d '{"command": "whoami"}'
```

### Running locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set your token
echo "BEARER_TOKEN=secret" > .env

# Start the server
./local-server.sh

# Or with a container
./local-server.sh --container
```

## CLI Usage

Two CLI tools are provided: `cli.py` (Python) and `cli.sh` (Bash).

```bash
# Set credentials
export BEARER_TOKEN=secret
export API_URL=http://localhost:8000  # optional, this is the default

# List available commands
./cli.py

# Run commands
./cli.py ls -l
./cli.py uname -a
./cli.py echo hello world
./cli.sh whoami
```

### Container CLI

Run the CLI from a container:

```bash
./container-cli.sh ls -l
./container-cli.sh uname -a
```

Or manually with podman:

```bash
podman run --rm --network host \
  -e API_URL=http://localhost:8000 \
  -e BEARER_TOKEN=secret \
  ghcr.io/jasonluther/webify-bash python cli.py ls -l
```

## API

### Execute a command

```
POST /execute
Authorization: Bearer <token>
Content-Type: application/json

{
  "command": "ls",
  "flags": ["-l"],
  "args": ["/tmp"]
}
```

Response:

```json
{
  "executed_command": "ls -l /tmp",
  "return_code": 0,
  "stdout": "total 0\n...",
  "stderr": ""
}
```

### List allowed commands

```
GET /commands
Authorization: Bearer <token>
```

### curl example

```bash
curl -X POST https://webify-bash-production.up.railway.app/execute \
  -H "Authorization: Bearer YOUR-TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command": "uname", "flags": ["-a"]}'
```

### API Docs

Interactive docs available at `/docs` when the server is running.

## Deploy to Railway

1. Go to [railway.app](https://railway.app) and sign up with GitHub
2. Create new project → Deploy from GitHub repo → select this repo
3. Add environment variable: `BEARER_TOKEN` = your secret token
4. Railway auto-deploys on every push to main

## Configuration

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `BEARER_TOKEN` | Authentication token (required) | - |
| `API_URL` | API URL for CLI tools | `http://localhost:8000` |
| `HOST` | Server bind address | `0.0.0.0` |
| `PORT` | Server port | `8000` |

## Adding Commands

Edit `ALLOWED_COMMANDS` in `app.py`:

```python
ALLOWED_COMMANDS = {
    "mycommand": {
        "flags": ["-a", "-b", "--verbose"],
        "bare_arg": True,  # whether files/paths are allowed
    },
}
```

## Security

- Commands are executed as a list (no shell interpolation)
- Only whitelisted commands and flags are allowed
- 30 second timeout on all commands
- Bearer token required for all endpoints

## License

MIT
