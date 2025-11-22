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
    client: WebelClient = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WebelEnergySensor(client, entry)])


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
        data = await self._client.async_get_energyusage()
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
        try:
            self._native_value = float(value_str)
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid energy value for %s: %s", today_str, value_str)
