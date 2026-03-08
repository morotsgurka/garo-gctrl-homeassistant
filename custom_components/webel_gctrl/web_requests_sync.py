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


def fetch_all_bookings(username: str | None = None, password: str | None = None) -> dict[str, Any] | None:
    """Fetch all bookings with the given credentials."""
    if username is not None and password is not None:
        _apply_credentials(username, password)
    return _wr.fetch_all_bookings()


def get_energyusage(
    username: str | None = None,
    password: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict[str, Any] | None:
    """Fetch raw energy JSON using provided credentials."""
    if username is not None and password is not None:
        _apply_credentials(username, password)
    return _wr.get_energyusage_raw(from_date=from_date, to_date=to_date)


def validate_credentials(username: str, password: str) -> bool:
    """Validate credentials against Webel Online in a blocking manner."""
    return _wr.validate_credentials(username, password)
