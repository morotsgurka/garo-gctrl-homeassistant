"""Binary sensor platform for Webel G-CTRL problems."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Webel problem binary sensor from a config entry."""
    _LOGGER.debug("Setting up Webel G-CTRL problem binary sensor for entry %s", entry.entry_id)
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: DataUpdateCoordinator = entry_data["state_coordinator"]

    sensor = WebelProblemBinarySensor(coordinator, entry)
    _LOGGER.debug(
        "Created Webel G-CTRL problem binary sensor entity with unique_id=%s",
        sensor.unique_id,
    )
    async_add_entities([sensor])


class WebelProblemBinarySensor(BinarySensorEntity):
    """Binary sensor that is on when there is a problem reaching Webel."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry.entry_id}_problem"
        self._attr_name = "Webel G-CTRL Problem"

    @property
    def is_on(self) -> bool:
        """Return True if there is a problem (no data / failed update)."""
        if not self._coordinator.last_update_success:
            return True

        data = self._coordinator.data or {}
        return not bool(data)

    async def async_update(self) -> None:
        """Request an updated state from the shared coordinator."""
        await self._coordinator.async_request_refresh()
