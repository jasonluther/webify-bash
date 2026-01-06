#!/usr/bin/env python3
"""FastAPI app for safely executing whitelisted shell commands."""

import os
import subprocess
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="Shell Command API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://jasonluther.github.io"],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

BEARER_TOKEN = os.getenv("BEARER_TOKEN")
if not BEARER_TOKEN:
    raise RuntimeError("BEARER_TOKEN must be set in environment")

# Command whitelist configuration
# Format: "command": {"flags": [allowed flags], "bare_arg": bool}
ALLOWED_COMMANDS = {
    "echo": {
        "flags": ["-n", "-e"],
        "bare_arg": True,
    },
    "ls": {
        "flags": ["-l", "-a", "-la", "-lh", "-alh", "-1", "-R"],
        "bare_arg": True,
    },
    "uname": {
        "flags": ["-a", "-s", "-n", "-r", "-v", "-m", "-p", "-o"],
        "bare_arg": False,
    },
    "whoami": {
        "flags": [],
        "bare_arg": False,
    },
}


class CommandRequest(BaseModel):
    command: str
    flags: Optional[list[str]] = None
    args: Optional[list[str]] = None  # bare arguments (files, paths, etc.)


class CommandResponse(BaseModel):
    executed_command: str
    return_code: int
    stdout: str
    stderr: str


def verify_token(authorization: str) -> bool:
    """Verify the bearer token."""
    if not authorization.startswith("Bearer "):
        return False
    token = authorization[7:]
    return token == BEARER_TOKEN


def validate_command(req: CommandRequest) -> list[str]:
    """Validate and build the command list safely."""
    if req.command not in ALLOWED_COMMANDS:
        raise HTTPException(status_code=400, detail=f"Command '{req.command}' is not allowed")

    config = ALLOWED_COMMANDS[req.command]
    cmd_list = [req.command]

    # Validate flags
    if req.flags:
        for flag in req.flags:
            # Handle flags with values like "-n 10"
            flag_parts = flag.split(None, 1)
            flag_name = flag_parts[0]

            if flag_name not in config["flags"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Flag '{flag_name}' is not allowed for command '{req.command}'"
                )
            cmd_list.extend(flag_parts)

    # Validate bare arguments
    if req.args:
        if not config["bare_arg"]:
            raise HTTPException(
                status_code=400,
                detail=f"Command '{req.command}' does not accept bare arguments"
            )
        cmd_list.extend(req.args)

    return cmd_list


@app.post("/execute", response_model=CommandResponse)
async def execute_command(
    request: CommandRequest,
    authorization: str = Header(..., description="Bearer token")
):
    """Execute a whitelisted shell command."""
    if not verify_token(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing bearer token")

    cmd_list = validate_command(request)

    # Execute command safely using list form (no shell injection)
    try:
        result = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Command timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return CommandResponse(
        executed_command=" ".join(cmd_list),
        return_code=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


@app.get("/commands")
async def list_commands(authorization: str = Header(...)):
    """List all allowed commands and their configurations."""
    if not verify_token(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing bearer token")
    return ALLOWED_COMMANDS


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
