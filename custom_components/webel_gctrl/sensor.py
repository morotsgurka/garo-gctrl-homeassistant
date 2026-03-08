"""Sensor platform for Webel G-CTRL energy."""
from __future__ import annotations

from datetime import date
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .webel_client import WebelClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Webel sensors from a config entry."""
    _LOGGER.debug("Setting up Webel G-CTRL sensors for entry %s", entry.entry_id)
    entry_data = hass.data[DOMAIN][entry.entry_id]
    client: WebelClient = entry_data["client"]
    coordinator = entry_data["state_coordinator"]

    energy_sensor = WebelEnergySensor(client, entry)
    _LOGGER.debug(
        "Created Webel G-CTRL energy sensor entity with unique_id=%s",
        energy_sensor.unique_id,
    )

    status_sensor = WebelStatusSensor(coordinator, entry)
    _LOGGER.debug(
        "Created Webel G-CTRL status sensor entity with unique_id=%s",
        status_sensor.unique_id,
    )

    async_add_entities([energy_sensor, status_sensor])


class WebelEnergySensor(SensorEntity):
    """Sensor reporting daily energy from Webel for use in Energy dashboard."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "kWh"

    def __init__(self, client: WebelClient, entry: ConfigEntry) -> None:
        self._client = client
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_energy"
        self._attr_name = "Webel G-CTRL Energy"
        self._native_value: float | None = None

    @property
    def native_value(self) -> float | None:
        return self._native_value

    async def async_update(self) -> None:
        """Fetch latest energy usage and update month-to-date total.

        The Webel API returns per-day kWh values for the current month.
        Home Assistant's Energy dashboard expects a total-increasing meter
        reading, so we sum all days in the current month up to today and
        expose that cumulative value. The Energy dashboard will then
        derive per-day usage from the differences.
        """
        _LOGGER.debug(
            "Requesting latest energy usage from Webel for entry %s", self._entry.entry_id
        )
        data = await self._client.async_get_energyusage()
        _LOGGER.debug("Energy usage response from Webel: %s", data)
        if not data:
            _LOGGER.debug("No energy data returned from Webel")
            return

        try:
            timestamps = data["timestamps"].split("|")
            values = data["values"].split("|")
            energy_map: dict[str, str] = dict(zip(timestamps, values))
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Failed to parse energy JSON: %s", err)
            return

        today = date.today()
        total = 0.0

        for ts, value_str in energy_map.items():
            try:
                day = date.fromisoformat(ts)
            except ValueError:
                _LOGGER.debug("Skipping invalid energy timestamp: %s", ts)
                continue

            # Only include days from the current month up to today
            if day.year != today.year or day.month != today.month or day > today:
                continue

            try:
                val = float(value_str)
            except (ValueError, TypeError):
                _LOGGER.debug("Skipping invalid energy value for %s: %s", ts, value_str)
                continue

            total += val

        self._native_value = total
        _LOGGER.debug(
            "Updated month-to-date energy total to %s kWh for %s",
            self._native_value,
            today,
        )


class WebelStatusSensor(SensorEntity):
    """Sensor reporting the current status/problem of the Webel integration."""

    _attr_icon = "mdi:alert-circle-outline"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        self._coordinator = coordinator
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_status"
        self._attr_name = "Webel G-CTRL Status"

    @property
    def native_value(self) -> str:
        """Return a human-readable status string based on coordinator state."""
        # If the last refresh failed, report the error
        if not self._coordinator.last_update_success:
            err = getattr(self._coordinator, "last_exception", None)
            if err:
                return f"Problem: {err}"
            return "Problem: Failed to fetch data from Webel Online"

        data = self._coordinator.data or {}
        if not data:
            return "Problem: No data received from Webel Online"

        return "All ok!"

    async def async_update(self) -> None:
        """Request an updated state from the shared coordinator."""
        await self._coordinator.async_request_refresh()
