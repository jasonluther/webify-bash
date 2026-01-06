#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load defaults first, then .env overrides
load_dotenv(Path(__file__).parent / "defaults.env")
load_dotenv(override=True)


def _get_env(key: str) -> str:
    """Get required environment variable or exit with clear error."""
    value = os.environ.get(key)
    if value is None:
        print(f"Error: {key} is required. Check defaults.env exists.", file=sys.stderr)
        sys.exit(1)
    return value


def _get_int(key: str) -> int:
    """Get integer environment variable or exit with clear error."""
    value = _get_env(key)
    try:
        return int(value)
    except ValueError:
        print(f"Error: {key} must be an integer, got '{value}'", file=sys.stderr)
        sys.exit(1)


class Config:
    BEARER_TOKEN: str = os.environ.get("BEARER_TOKEN", "")
    PORT: int = _get_int("PORT")
    HOST: str = _get_env("HOST")
    COMMAND_TIMEOUT: int = _get_int("COMMAND_TIMEOUT")
    ALLOWED_ORIGINS: list[str] = [
        origin.strip() for origin in _get_env("ALLOWED_ORIGINS").split(",") if origin.strip()
    ]
    CONTAINER_NAME: str = _get_env("CONTAINER_NAME")
    LOCAL_IMAGE_NAME: str = _get_env("LOCAL_IMAGE_NAME")
    GHCR_IMAGE: str = _get_env("GHCR_IMAGE")
    COMMANDS_FILE: Path = Path(__file__).parent / _get_env("COMMANDS_FILE")

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration. Exit if invalid."""
        if not cls.BEARER_TOKEN:
            print("Error: BEARER_TOKEN is required in .env", file=sys.stderr)
            sys.exit(1)


config = Config()
