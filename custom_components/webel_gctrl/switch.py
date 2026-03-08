"""Switch platform for Webel G-CTRL."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .webel_client import WebelClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Webel switch from a config entry."""
    _LOGGER.debug("Setting up Webel G-CTRL switch for entry %s", entry.entry_id)
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: DataUpdateCoordinator = entry_data["state_coordinator"]
    client: WebelClient = entry_data["client"]

    _LOGGER.debug("Initial switch state after first refresh: %s", coordinator.data)

    entity = WebelSwitch(coordinator, client, entry)
    _LOGGER.debug("Created Webel G-CTRL switch entity with unique_id=%s", entity.unique_id)
    async_add_entities([entity])


class WebelSwitch(SwitchEntity):
    """Representation of the Webel outlet as a switch."""

    _attr_icon = "mdi:power-plug"
    _attr_device_class = SwitchDeviceClass.OUTLET

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        client: WebelClient,
        entry: ConfigEntry,
    ) -> None:
        self._coordinator = coordinator
        self._client = client
        self._attr_unique_id = f"{entry.entry_id}_switch"
        self._attr_name = "Webel G-CTRL Outlet"

    @property
    def available(self) -> bool:
        return self._coordinator.last_update_success

    @property
    def is_on(self) -> bool:
        data = self._coordinator.data or {}
        _LOGGER.debug("Switch is_on check, coordinator data: %s", data)
        return bool(data.get("on"))

    @property
    def extra_state_attributes(self):
        data = self._coordinator.data or {}
        _LOGGER.debug("Switch extra_state_attributes, coordinator data: %s", data)
        return {"until": data.get("until")}

    async def async_turn_on(self, **kwargs) -> None:  # type: ignore[override]
        _LOGGER.debug("Turning ON Webel G-CTRL switch %s", self.unique_id)
        await self._client.async_turn_on()
        await self._coordinator.async_request_refresh()
        _LOGGER.debug("Requested refresh after turning ON Webel G-CTRL switch %s", self.unique_id)

    async def async_turn_off(self, **kwargs) -> None:  # type: ignore[override]
        _LOGGER.debug("Turning OFF Webel G-CTRL switch %s", self.unique_id)
        await self._client.async_turn_off()
        await self._coordinator.async_request_refresh()
        _LOGGER.debug("Requested refresh after turning OFF Webel G-CTRL switch %s", self.unique_id)

    async def async_update(self) -> None:
        _LOGGER.debug("Manual update requested for Webel G-CTRL switch %s", self.unique_id)
        await self._coordinator.async_request_refresh()
