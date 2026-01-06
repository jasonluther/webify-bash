#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    # Required - no default
    BEARER_TOKEN: str = os.getenv("BEARER_TOKEN", "")

    # Server settings
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    COMMAND_TIMEOUT: int = int(os.getenv("COMMAND_TIMEOUT", "30"))

    # CORS - comma-separated list of origins
    ALLOWED_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS", "https://jasonluther.github.io"
        ).split(",")
        if origin.strip()
    ]

    # Container settings
    CONTAINER_NAME: str = os.getenv("CONTAINER_NAME", "webify-bash")
    LOCAL_IMAGE_NAME: str = os.getenv("LOCAL_IMAGE_NAME", "webify-bash")
    GHCR_IMAGE: str = os.getenv("GHCR_IMAGE", "ghcr.io/jasonluther/webify-bash:latest")

    # Commands config file
    COMMANDS_FILE: Path = Path(
        os.getenv("COMMANDS_FILE", str(Path(__file__).parent / "commands.json"))
    )

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration. Exit if invalid."""
        if not cls.BEARER_TOKEN:
            print("Error: BEARER_TOKEN is required", file=sys.stderr)
            sys.exit(1)


config = Config()
