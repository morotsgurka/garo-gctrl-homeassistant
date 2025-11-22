"""Config flow for Webel G-CTRL."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN


class WebelConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Webel G-CTRL."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input["username"], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required("username"): str,
                vol.Required("password"): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
