"""Switch platform for Webel G-CTRL."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .webel_client import WebelClient

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Webel switch from a config entry."""
    client: WebelClient = hass.data[DOMAIN][entry.entry_id]

    async def async_update_data():
        try:
            return await client.async_check_state()
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(str(err)) from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="webel_gctrl_switch",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    entity = WebelSwitch(coordinator, client, entry)
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
        return bool(data.get("on"))

    @property
    def extra_state_attributes(self):
        data = self._coordinator.data or {}
        return {"until": data.get("until")}

    async def async_turn_on(self, **kwargs) -> None:  # type: ignore[override]
        await self._client.async_turn_on()
        await self._coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:  # type: ignore[override]
        await self._client.async_turn_off()
        await self._coordinator.async_request_refresh()

    async def async_update(self) -> None:
        await self._coordinator.async_request_refresh()
