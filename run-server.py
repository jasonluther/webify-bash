#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

IMAGE_NAME = "webify-bash"
GHCR_IMAGE = "ghcr.io/jasonluther/webify-bash:latest"
CONTAINER_NAME = "webify-bash"
PORT = os.environ.get("PORT", "8000")


def load_env():
    """Load .env file and return dict of values."""
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("Error: .env file not found", file=sys.stderr)
        sys.exit(1)

    env = {}
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()

    if "BEARER_TOKEN" not in env or not env["BEARER_TOKEN"]:
        print("Error: BEARER_TOKEN not set in .env", file=sys.stderr)
        sys.exit(1)

    return env


def find_container_runtime():
    """Find podman or docker, preferring podman."""
    for cmd in ["podman", "docker"]:
        if shutil.which(cmd):
            return cmd
    print("Error: podman or docker required", file=sys.stderr)
    sys.exit(1)


def run_cmd(args, check=True):
    """Print and run a command."""
    print(f"$ {' '.join(args)}")
    return subprocess.run(args, check=check)


def start_uvicorn(env):
    """Start server with uvicorn (no container)."""
    cmd = ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", PORT]
    print(f"Starting server at http://localhost:{PORT}")
    run_cmd(cmd)


def start_container(runtime, image, env, build=False):
    """Start server in container."""
    if build:
        run_cmd([runtime, "build", "-t", IMAGE_NAME, "."])
        image = IMAGE_NAME

    # Stop existing container if running
    subprocess.run(
        [runtime, "stop", CONTAINER_NAME],
        capture_output=True,
    )
    subprocess.run(
        [runtime, "rm", CONTAINER_NAME],
        capture_output=True,
    )

    if image == GHCR_IMAGE:
        run_cmd([runtime, "pull", image])

    cmd = [
        runtime,
        "run",
        "--rm",
        "--name",
        CONTAINER_NAME,
        "-p",
        f"{PORT}:8000",
        "-e",
        f"BEARER_TOKEN={env['BEARER_TOKEN']}",
        image,
    ]
    print(f"Starting container at http://localhost:{PORT}")
    run_cmd(cmd)


def stop_container(runtime):
    """Stop running container."""
    result = run_cmd([runtime, "stop", CONTAINER_NAME], check=False)
    if result.returncode != 0:
        print(f"Container '{CONTAINER_NAME}' is not running")


def main():
    parser = argparse.ArgumentParser(
        description="Run the webify-bash server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Start with GitHub container image (default)
  %(prog)s --uvicorn          # Start with uvicorn (no container)
  %(prog)s --local-container  # Build and start local container
  %(prog)s stop               # Stop running container
""",
    )

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--uvicorn",
        action="store_true",
        help="Run with uvicorn (no container)",
    )
    mode.add_argument(
        "--local-container",
        action="store_true",
        help="Build and run local container",
    )
    mode.add_argument(
        "--ghcr-container",
        action="store_true",
        default=True,
        help="Run GitHub container image (default)",
    )

    parser.add_argument(
        "command",
        nargs="?",
        choices=["start", "stop"],
        default="start",
        help="Command to run (default: start)",
    )

    args = parser.parse_args()

    # Handle mutually exclusive group quirk
    if args.uvicorn or args.local_container:
        args.ghcr_container = False

    if args.command == "stop":
        runtime = find_container_runtime()
        stop_container(runtime)
        return

    env = load_env()

    if args.uvicorn:
        start_uvicorn(env)
    else:
        runtime = find_container_runtime()
        if args.local_container:
            start_container(runtime, IMAGE_NAME, env, build=True)
        else:
            start_container(runtime, GHCR_IMAGE, env, build=False)


if __name__ == "__main__":
    main()
