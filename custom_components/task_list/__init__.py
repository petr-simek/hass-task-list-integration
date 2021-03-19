from .sensor import TASK_ADD_SCHEMA, TASK_DELETE_SCHEMA, TASK_UPDATE_SCHEMA
from homeassistant.config_entries import ConfigEntry
import logging
from homeassistant.core import (
    HomeAssistant,
)
from . import sensor
from .const import DOMAIN, TASK_LIST_ID, TASK_ID
from .config_flow import DATA_SCHEMA

_LOGGER = logging.getLogger(__name__)

SERVICE_ADD_TASK = "service_add_task"
SERVICE_UPDATE_TASK = "service_update_task"
SERVICE_DELETE_TASK = "service_delete_task"
SERVICE_DELETE_DONE_ITEMS = "service_delete_done_items"


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Hello World component."""
    hass.data.setdefault(DOMAIN, {})

    def add_task(call):
        task_list = hass.data[DOMAIN].get(call.data[TASK_LIST_ID])
        task_list.add_task(call.data.copy())

    def update_task(call):
        task_list = hass.data[DOMAIN].get(call.data[TASK_LIST_ID])
        task_list.update_task(call.data.copy())

    def delete_task(call):
        task_list = hass.data[DOMAIN].get(call.data[TASK_LIST_ID])
        task_list.delete_task(call.data.copy())

    def delete_task_items(call):
        task_list = hass.data[DOMAIN].get(call.data[TASK_LIST_ID])
        task_list.delete_task_items(call.data[TASK_ID])

    hass.services.async_register(DOMAIN, SERVICE_ADD_TASK, add_task, schema=TASK_ADD_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_UPDATE_TASK, update_task, schema=TASK_UPDATE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_DELETE_TASK, delete_task, schema=TASK_DELETE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_DELETE_DONE_ITEMS, delete_task_items, schema=TASK_DELETE_SCHEMA)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hello World from a config entry."""
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)

    return True
