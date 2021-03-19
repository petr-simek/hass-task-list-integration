import logging

import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from homeassistant.core import callback
from .const import (
    DOMAIN,
    CONF_USER,
    CONF_NAME
)  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)


class TaskListService:

    @callback
    def add_task(self, call):
        """My first service."""
        _LOGGER.info('Received data', call.data)
