"""Webel G-CTRL integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .webel_client import WebelClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["switch", "calendar", "sensor", "binary_sensor"]

SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Webel G-CTRL from a config entry."""
    _LOGGER.debug("Webel G-CTRL integration setup starting for entry %s", entry.entry_id)
    username = entry.data["username"]
    password = entry.data["password"]

    client = WebelClient(username, password)

    async def async_update_data() -> dict:
        try:
            return await client.async_check_state()
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(str(err)) from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="webel_gctrl_state",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "state_coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.debug("Webel G-CTRL integration setup complete for entry %s", entry.entry_id)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
