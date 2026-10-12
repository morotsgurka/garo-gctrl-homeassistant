"""Constants for the Webel G-CTRL integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo

DOMAIN = "webel_gctrl"


def get_device_info(entry: ConfigEntry) -> DeviceInfo:
	"""Return shared device information for all entities in this entry."""
	return DeviceInfo(
		identifiers={(DOMAIN, entry.entry_id)},
		name="Webel G-CTRL",
	)
