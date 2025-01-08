from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # Validate and save user input
            username = user_input['username']
            password = user_input['password']

            # Check if the password and password confirmation match
            if password != user_input['password_confirmation']:
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema(
                        {
                            "username": str,
                            "password": str,
                            "password_confirmation": str,
                        }
                    ),
                    errors={"base": "Passwords do not match."},
                )

            # Store the configuration
            return self.async_create_entry(
                title=username,
                data={"username": username, "password": password},
            )

        # Show the form for user input
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    "username": str,
                    "password": str,
                    "password_confirmation": str,
                }
            ),
        )
