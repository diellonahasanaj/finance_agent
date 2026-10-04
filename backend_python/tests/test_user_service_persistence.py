"""Tests for file-backed user persistence and datetime restoration."""
import json
from datetime import datetime

import pytest

from app.services import user_service


def test_load_users_restores_datetime_fields(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    users_file.write_text(json.dumps({
        "test@example.com": {
            "_id": "1",
            "name": "Test User",
            "email": "test@example.com",
            "created_at": "2026-10-01T10:00:00",
            "last_login": "2026-10-02T10:00:00",
            "verification_expires": "2026-10-05T10:00:00",
            "locked_until": "2026-10-04T11:00:00",
            "password_reset_expires": "2026-10-04T12:00:00",
        }
    }), encoding="utf-8")
    monkeypatch.setattr(user_service, "USERS_FILE", str(users_file))

    users = user_service.load_users()
    user = users["test@example.com"]

    assert isinstance(user["created_at"], datetime)
    assert isinstance(user["last_login"], datetime)
    assert isinstance(user["verification_expires"], datetime)
    assert isinstance(user["locked_until"], datetime)
    assert isinstance(user["password_reset_expires"], datetime)


def test_load_users_returns_empty_when_file_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(user_service, "USERS_FILE", str(tmp_path / "missing.json"))
    assert user_service.load_users() == {}
