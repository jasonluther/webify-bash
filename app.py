#!/usr/bin/env python3
import json
import os
import subprocess
from pathlib import Path
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

COMMANDS_FILE = Path(__file__).parent / "commands.json"
ALLOWED_COMMANDS = json.loads(COMMANDS_FILE.read_text())


class CommandRequest(BaseModel):
    command: str
    flags: Optional[list[str]] = None
    args: Optional[list[str]] = None


class CommandResponse(BaseModel):
    executed_command: str
    return_code: int
    stdout: str
    stderr: str


def verify_token(authorization: str) -> bool:
    if not authorization.startswith("Bearer "):
        return False
    return authorization[7:] == BEARER_TOKEN


def validate_command(req: CommandRequest) -> list[str]:
    if req.command not in ALLOWED_COMMANDS:
        raise HTTPException(
            status_code=400, detail=f"Command '{req.command}' is not allowed"
        )

    config = ALLOWED_COMMANDS[req.command]
    cmd_list = [req.command]

    if req.flags:
        for flag in req.flags:
            flag_parts = flag.split(None, 1)
            if flag_parts[0] not in config["flags"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Flag '{flag_parts[0]}' is not allowed for command '{req.command}'",
                )
            cmd_list.extend(flag_parts)

    if req.args:
        if not config["bare_arg"]:
            raise HTTPException(
                status_code=400,
                detail=f"Command '{req.command}' does not accept arguments",
            )
        cmd_list.extend(req.args)

    return cmd_list


@app.post("/execute", response_model=CommandResponse)
def execute_command(request: CommandRequest, authorization: str = Header(...)):
    if not verify_token(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing bearer token")

    cmd_list = validate_command(request)

    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, timeout=30)
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
def list_commands(authorization: str = Header(...)):
    if not verify_token(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing bearer token")
    return ALLOWED_COMMANDS


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
