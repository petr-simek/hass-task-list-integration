import logging

import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from .const import (
    DOMAIN,
    CONF_USER,
    CONF_NAME
)  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): str,
    vol.Optional(CONF_USER): vol.In([1, 2]),
})


async def validate_input(hass: core.HomeAssistant, data: dict):
    if len(data["name"]) < 3:
        raise InvalidName

    return {"title": data["name"]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hello World."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        errors = {}
        name = ""
        user = None
        if user_input is not None:
            if "name" in user_input:
                name = user_input["name"]
            if "user" in user_input:
                user = user_input["user"]

            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except InvalidName:
                errors["name"] = "invalid_name"
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception", e)
                errors["base"] = "unknown"

        users = [user]
        for collection in self.hass.data["person"]:
            for item in collection.async_items():
                users.append(item["name"])

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({
                vol.Required(CONF_NAME, default=name): str,
                vol.Optional(CONF_USER, default=user): vol.In(users),
            }), errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidName(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
