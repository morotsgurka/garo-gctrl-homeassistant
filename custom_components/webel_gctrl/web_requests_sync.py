"""Slightly adapted sync wrapper around your existing web_requests.py."""

from __future__ import annotations

from typing import Any

from . import web_requests as _wr


def _apply_credentials(username: str, password: str) -> None:
    _wr.login_payload["username"] = username
    _wr.login_payload["password"] = password


def turn_on(minutes: int = 120, username: str | None = None, password: str | None = None) -> bool:
    if username is not None and password is not None:
        _apply_credentials(username, password)
    return bool(_wr.turn_on(minutes))


def turn_off(username: str | None = None, password: str | None = None) -> bool:
    if username is not None and password is not None:
        _apply_credentials(username, password)
    return bool(_wr.turn_off())


def check_state(username: str | None = None, password: str | None = None) -> dict[str, Any]:
    if username is not None and password is not None:
        _apply_credentials(username, password)
    return _wr.check_state()
