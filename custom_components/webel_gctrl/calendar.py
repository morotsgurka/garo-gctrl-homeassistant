"""Calendar platform for Webel G-CTRL bookings."""
from __future__ import annotations

from datetime import datetime, timedelta, time
import logging
from typing import Iterable, List

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .webel_client import WebelClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Webel calendar from a config entry."""
    client: WebelClient = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WebelCalendar(client, entry)])


class WebelCalendar(CalendarEntity):
    """Calendar entity that exposes Webel bookings as events."""

    def __init__(self, client: WebelClient, entry: ConfigEntry) -> None:
        self._client = client
        self._entry = entry
        self._events: list[CalendarEvent] = []
        self._attr_unique_id = f"{entry.entry_id}_calendar"
        self._attr_name = "Webel G-CTRL Bookings"

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event for the calendar state."""
        if not self._events:
            return None

        now = dt_util.utcnow()
        upcoming = [e for e in self._events if e.start and e.start >= now]

        if upcoming:
            return min(upcoming, key=lambda e: e.start)

        # Fallback: return earliest event we have
        return min(self._events, key=lambda e: e.start or now)

    async def async_update(self) -> None:
        """Fetch and parse bookings into events."""
        data = await self._client.async_fetch_bookings()
        self._events = parse_bookings_to_events(data)

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return events occurring in the given time range."""
        # Ensure we have fresh data
        await self.async_update()
        return [
            event
            for event in self._events
            if event.start is not None
            and event.end is not None
            and event.end > start_date
            and event.start < end_date
        ]


def parse_bookings_to_events(data: dict | None) -> list[CalendarEvent]:
    """Parse Webel booking strings into CalendarEvent objects.

    booking_strings look like: "000-000-017-173-A2-1-6;21:00"
    We interpret the last number as weekday (1=Mon..7=Sun) and the time part
    as HH:MM, and create events for the *next* such weekday in the future.
    Each event is given a fixed 1-hour duration.
    """
    if not data:
        return []

    try:
        booking_strings: Iterable[str] = data.get("booking_strings", [])
    except AttributeError:
        return []

    now = dt_util.utcnow()
    events: list[CalendarEvent] = []

    for raw in booking_strings:
        try:
            # Split id/day/time portion
            id_part, time_part = raw.split(";")
            # id_part like "000-000-017-173-A2-1-6" -> day is last segment
            parts = id_part.split("-")
            day_str = parts[-1]
            weekday = int(day_str)  # 1=Mon..7=Sun
            hour_str, minute_str = time_part.split(":")
            hh = int(hour_str)
            mm = int(minute_str)
        except Exception:  # noqa: BLE001
            _LOGGER.debug("Failed to parse booking string: %s", raw)
            continue

        event_start = next_weekday_datetime(now, weekday, time(hh, mm))
        event_end = event_start + timedelta(hours=1)

        # Simple title: "Scheduled departure"; could be improved later
        events.append(
            CalendarEvent(
                summary="Webel booking",
                start=event_start,
                end=event_end,
            )
        )

    return events


def next_weekday_datetime(
    ref: datetime,
    weekday_1_7: int,
    at_time: time,
) -> datetime:
    """Return the next datetime at given weekday (1=Mon..7=Sun) and time.

    If the computed time is earlier than 'ref', we move to the next week.
    """
    # Home Assistant / Python weekday: Monday=0..Sunday=6
    target_py = (weekday_1_7 - 1) % 7

    ref_local = dt_util.as_local(ref)
    days_ahead = (target_py - ref_local.weekday()) % 7
    candidate = datetime.combine(
        (ref_local + timedelta(days=days_ahead)).date(),
        at_time,
        tzinfo=ref_local.tzinfo,
    )
    if candidate <= ref_local:
        candidate = candidate + timedelta(days=7)

    # Convert back to UTC for storage in events
    return dt_util.as_utc(candidate)
