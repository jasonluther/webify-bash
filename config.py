#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load defaults first, then .env overrides
load_dotenv(Path(__file__).parent / "defaults.env")
load_dotenv(override=True)


class Config:
    BEARER_TOKEN: str = os.environ.get("BEARER_TOKEN", "")
    PORT: int = int(os.environ["PORT"])
    HOST: str = os.environ["HOST"]
    COMMAND_TIMEOUT: int = int(os.environ["COMMAND_TIMEOUT"])
    ALLOWED_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.environ["ALLOWED_ORIGINS"].split(",")
        if origin.strip()
    ]
    CONTAINER_NAME: str = os.environ["CONTAINER_NAME"]
    LOCAL_IMAGE_NAME: str = os.environ["LOCAL_IMAGE_NAME"]
    GHCR_IMAGE: str = os.environ["GHCR_IMAGE"]
    COMMANDS_FILE: Path = Path(__file__).parent / os.environ["COMMANDS_FILE"]

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration. Exit if invalid."""
        if not cls.BEARER_TOKEN:
            print("Error: BEARER_TOKEN is required in .env", file=sys.stderr)
            sys.exit(1)


config = Config()
