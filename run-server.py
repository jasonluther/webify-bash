#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from config import config


def find_container_runtime() -> str:
    """Find podman or docker, preferring podman."""
    for cmd in ["podman", "docker"]:
        if shutil.which(cmd):
            return cmd
    print("Error: podman or docker required", file=sys.stderr)
    sys.exit(1)


def run_cmd(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Print and run a command."""
    print(f"$ {' '.join(args)}")
    return subprocess.run(args, check=check)


def start_uvicorn() -> None:
    """Start server with uvicorn (no container)."""
    config.validate()
    cmd = ["uvicorn", "app:app", "--host", config.HOST, "--port", str(config.PORT)]
    print(f"Starting server at http://localhost:{config.PORT}")
    run_cmd(cmd)


def start_container(runtime: str, image: str, build: bool = False) -> None:
    """Start server in container."""
    config.validate()

    if build:
        run_cmd([runtime, "build", "-t", config.LOCAL_IMAGE_NAME, "."])
        image = config.LOCAL_IMAGE_NAME

    # Stop existing container if running
    subprocess.run([runtime, "stop", config.CONTAINER_NAME], capture_output=True)
    subprocess.run([runtime, "rm", config.CONTAINER_NAME], capture_output=True)

    if image == config.GHCR_IMAGE:
        run_cmd([runtime, "pull", image])

    # Write env file to avoid exposing secrets in process list
    # Use os.open with O_CREAT|O_EXCL to create file atomically with restricted permissions
    env_content = f"""BEARER_TOKEN={config.BEARER_TOKEN}
COMMAND_TIMEOUT={config.COMMAND_TIMEOUT}
ALLOWED_ORIGINS={",".join(config.ALLOWED_ORIGINS)}
"""
    env_file = Path(tempfile.gettempdir()) / f".webify-bash-{config.CONTAINER_NAME}.env"
    env_file.unlink(missing_ok=True)  # Remove if exists from previous run
    fd = os.open(env_file, os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        os.write(fd, env_content.encode())
    finally:
        os.close(fd)

    cmd = [
        runtime,
        "run",
        "--rm",
        "--name",
        config.CONTAINER_NAME,
        "-p",
        f"{config.PORT}:8000",
        "--env-file",
        str(env_file),
        image,
    ]
    print(f"Starting container at http://localhost:{config.PORT}")
    try:
        run_cmd(cmd)
    finally:
        env_file.unlink(missing_ok=True)


def stop_container(runtime: str) -> None:
    """Stop running container."""
    result = run_cmd([runtime, "stop", config.CONTAINER_NAME], check=False)
    if result.returncode != 0:
        print(f"Container '{config.CONTAINER_NAME}' is not running")


def main() -> None:
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

    if args.uvicorn:
        start_uvicorn()
    else:
        runtime = find_container_runtime()
        if args.local_container:
            start_container(runtime, config.LOCAL_IMAGE_NAME, build=True)
        else:
            start_container(runtime, config.GHCR_IMAGE, build=False)


if __name__ == "__main__":
    main()
