import os
import pytest
from unittest.mock import patch

os.environ["BEARER_TOKEN"] = "test-token"

from fastapi.testclient import TestClient
from app import app, verify_token, validate_command, CommandRequest, ALLOWED_COMMANDS


client = TestClient(app)


class TestVerifyToken:
    def test_valid_token(self):
        assert verify_token("Bearer test-token") is True

    def test_invalid_token(self):
        assert verify_token("Bearer wrong-token") is False

    def test_missing_bearer_prefix(self):
        assert verify_token("test-token") is False

    def test_empty_string(self):
        assert verify_token("") is False


class TestValidateCommand:
    def test_valid_command(self):
        req = CommandRequest(command="ls", flags=["-l"], args=["/tmp"])
        result = validate_command(req)
        assert result == ["ls", "-l", "/tmp"]

    def test_command_without_flags_or_args(self):
        req = CommandRequest(command="whoami")
        result = validate_command(req)
        assert result == ["whoami"]

    def test_invalid_command(self):
        req = CommandRequest(command="rm")
        with pytest.raises(Exception) as exc:
            validate_command(req)
        assert "not allowed" in str(exc.value.detail)

    def test_invalid_flag(self):
        req = CommandRequest(command="ls", flags=["--delete"])
        with pytest.raises(Exception) as exc:
            validate_command(req)
        assert "not allowed" in str(exc.value.detail)

    def test_args_not_allowed(self):
        req = CommandRequest(command="whoami", args=["/tmp"])
        with pytest.raises(Exception) as exc:
            validate_command(req)
        assert "does not accept arguments" in str(exc.value.detail)

    def test_multiple_flags(self):
        req = CommandRequest(command="ls", flags=["-l", "-a"])
        result = validate_command(req)
        assert result == ["ls", "-l", "-a"]


class TestExecuteEndpoint:
    def test_success(self):
        response = client.post(
            "/execute",
            json={"command": "echo", "args": ["hello"]},
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["return_code"] == 0
        assert "hello" in data["stdout"]

    def test_unauthorized(self):
        response = client.post(
            "/execute",
            json={"command": "whoami"},
            headers={"Authorization": "Bearer wrong"}
        )
        assert response.status_code == 401

    def test_missing_auth(self):
        response = client.post("/execute", json={"command": "whoami"})
        assert response.status_code == 422

    def test_invalid_command(self):
        response = client.post(
            "/execute",
            json={"command": "rm", "args": ["-rf", "/"]},
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 400


class TestCommandsEndpoint:
    def test_list_commands(self):
        response = client.get(
            "/commands",
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "ls" in data
        assert "echo" in data
        assert data["ls"]["bare_arg"] is True

    def test_unauthorized(self):
        response = client.get(
            "/commands",
            headers={"Authorization": "Bearer wrong"}
        )
        assert response.status_code == 401
