"""Thin async wrapper around the web_requests logic."""

from __future__ import annotations

import asyncio
from functools import partial

from . import web_requests_sync


class WebelClient:
    """Client exposing async helpers for Webel operations."""

    def __init__(self, username: str, password: str) -> None:
        self._username = username
        self._password = password

    async def async_turn_on(self, minutes: int = 120) -> bool:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            partial(web_requests_sync.turn_on, minutes=minutes, username=self._username, password=self._password),
        )

    async def async_turn_off(self) -> bool:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            partial(web_requests_sync.turn_off, username=self._username, password=self._password),
        )

    async def async_check_state(self) -> dict:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            partial(web_requests_sync.check_state, username=self._username, password=self._password),
        )

    async def async_fetch_bookings(self) -> dict | None:
        """Fetch all bookings for this client."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            partial(web_requests_sync.fetch_all_bookings, username=self._username, password=self._password),
        )

    async def async_get_energyusage(self) -> dict | None:
        """Fetch energy usage JSON for the current month."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            partial(web_requests_sync.get_energyusage, username=self._username, password=self._password),
        )
