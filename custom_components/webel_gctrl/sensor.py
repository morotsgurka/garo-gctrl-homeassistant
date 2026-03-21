"""Sensor platform for Webel G-CTRL energy."""
from __future__ import annotations

from datetime import date
import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Webel sensors from a config entry."""
    _LOGGER.debug("Setting up Webel G-CTRL sensors for entry %s", entry.entry_id)
    entry_data = hass.data[DOMAIN][entry.entry_id]
    state_coordinator: DataUpdateCoordinator = entry_data["state_coordinator"]
    energy_coordinator: DataUpdateCoordinator = entry_data["energy_coordinator"]

    energy_sensor = WebelEnergySensor(energy_coordinator, entry)
    _LOGGER.debug(
        "Created Webel G-CTRL energy sensor entity with unique_id=%s",
        energy_sensor.unique_id,
    )

    status_sensor = WebelStatusSensor(state_coordinator, entry)
    _LOGGER.debug(
        "Created Webel G-CTRL status sensor entity with unique_id=%s",
        status_sensor.unique_id,
    )

    async_add_entities([energy_sensor, status_sensor])


class WebelEnergySensor(CoordinatorEntity[DataUpdateCoordinator], SensorEntity):
    """Sensor reporting daily energy from Webel for use in Energy dashboard."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "kWh"

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_energy"
        self._attr_name = "Webel G-CTRL Energy"

    @property
    def native_value(self) -> float | None:
        """Return month-to-date cumulative energy in kWh.

        The Webel API returns per-day values. We sum days in the current month
        up to today to expose a total-increasing reading for Energy dashboard.
        """
        data = self.coordinator.data or {}
        if not data:
            return None

        try:
            timestamps = data["timestamps"].split("|")
            values = data["values"].split("|")
            energy_map: dict[str, str] = dict(zip(timestamps, values))
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Failed to parse energy JSON: %s", err)
            return None

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

        return total


class WebelStatusSensor(CoordinatorEntity[DataUpdateCoordinator], SensorEntity):
    """Sensor reporting the current status/problem of the Webel integration."""

    _attr_icon = "mdi:alert-circle-outline"

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
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

