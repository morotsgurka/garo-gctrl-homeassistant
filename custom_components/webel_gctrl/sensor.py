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
    _LOGGER.debug("Setting up Webel G-CTRL energy sensor for entry %s", entry.entry_id)
    client: WebelClient = hass.data[DOMAIN][entry.entry_id]
    sensor = WebelEnergySensor(client, entry)
    _LOGGER.debug(
        "Created Webel G-CTRL energy sensor entity with unique_id=%s", sensor.unique_id
    )
    async_add_entities([sensor])


class WebelEnergySensor(SensorEntity):
    """Sensor reporting daily energy from Webel for use in Energy dashboard."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "kWh"

    def __init__(self, client: WebelClient, entry: ConfigEntry) -> None:
        self._client = client
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_energy"
        self._attr_name = "Webel G-CTRL Daily Energy"
        self._native_value: float | None = None

    @property
    def native_value(self) -> float | None:
        return self._native_value

    async def async_update(self) -> None:
        """Fetch latest energy usage and update today's value."""
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

        today_str = date.today().isoformat()
        value_str = energy_map.get(today_str, "0")
        _LOGGER.debug("Energy value for %s is %s", today_str, value_str)
        try:
            self._native_value = float(value_str)
            _LOGGER.debug(
                "Updated native energy value for %s to %s",
                today_str,
                self._native_value,
            )
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid energy value for %s: %s", today_str, value_str)
