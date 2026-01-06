#!/usr/bin/env python3
import argparse
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")


def list_commands():
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    try:
        response = requests.get(f"{API_URL}/commands", headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print("Available commands:")
    for cmd, config in sorted(response.json().items()):
        flags = " ".join(config["flags"]) if config["flags"] else "(none)"
        bare = "yes" if config["bare_arg"] else "no"
        print(f"  {cmd}: flags=[{flags}] args={bare}")


def main():
    parser = argparse.ArgumentParser(usage="%(prog)s [command] [flags...] [args...]")
    parser.add_argument("command", nargs="?", help="Command to execute")
    parser.add_argument("rest", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if not BEARER_TOKEN:
        print("Error: BEARER_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    if not args.command:
        list_commands()
        sys.exit(0)

    flags = [x for x in args.rest if x.startswith("-")]
    cmd_args = [x for x in args.rest if not x.startswith("-")]

    payload = {"command": args.command}
    if flags:
        payload["flags"] = flags
    if cmd_args:
        payload["args"] = cmd_args

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(f"{API_URL}/execute", json=payload, headers=headers)
    except requests.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if response.status_code != 200:
        print(
            f"Error: {response.json().get('detail', 'Unknown error')}", file=sys.stderr
        )
        sys.exit(1)

    data = response.json()
    print(data["stdout"], end="")
    print(data["stderr"], end="", file=sys.stderr)
    sys.exit(data["return_code"])


if __name__ == "__main__":
    main()
