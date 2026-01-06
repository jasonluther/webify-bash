#!/usr/bin/env python3
import json
import subprocess
from typing import Optional

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import config

config.validate()

app = FastAPI(title="Shell Command API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

ALLOWED_COMMANDS = json.loads(config.COMMANDS_FILE.read_text())


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
    return authorization[7:] == config.BEARER_TOKEN


def validate_command(req: CommandRequest) -> list[str]:
    if req.command not in ALLOWED_COMMANDS:
        raise HTTPException(
            status_code=400, detail=f"Command '{req.command}' is not allowed"
        )

    cmd_config = ALLOWED_COMMANDS[req.command]
    cmd_list = [req.command]

    if req.flags:
        for flag in req.flags:
            flag_parts = flag.split(None, 1)
            if flag_parts[0] not in cmd_config["flags"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Flag '{flag_parts[0]}' is not allowed for command '{req.command}'",
                )
            cmd_list.extend(flag_parts)

    if req.args:
        if not cmd_config["bare_arg"]:
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
        result = subprocess.run(
            cmd_list, capture_output=True, text=True, timeout=config.COMMAND_TIMEOUT
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
def list_commands(authorization: str = Header(...)):
    if not verify_token(authorization):
        raise HTTPException(status_code=401, detail="Invalid or missing bearer token")
    return ALLOWED_COMMANDS


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.HOST, port=config.PORT)
