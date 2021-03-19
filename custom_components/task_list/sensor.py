from homeassistant.helpers.entity import Entity, generate_entity_id
from homeassistant.helpers.restore_state import RestoreEntity, RestoreStateData
from .const import (
    DOMAIN,
    ATTR_TASKS,
    TASK_NAME,
    TASK_DESCRIPTION,
    TASK_DUE_DATE,
    TASK_DONE,
    TASK_ITEM, TASK_ID,
    TASK_LIST_ID,
    TASK_POSITION
)
import asyncio
import voluptuous as vol
from homeassistant.util.json import load_json, save_json
from homeassistant.helpers import config_validation as cv, discovery
from homeassistant.helpers import entity_component

TASK_ADD_SCHEMA = vol.Schema({
    vol.Required(TASK_NAME): vol.All(cv.string, vol.Length(min=1)),
    vol.Required(TASK_LIST_ID): str,
    vol.Required(TASK_DONE): bool,
    vol.Optional(TASK_DESCRIPTION): str,
    vol.Optional(TASK_DUE_DATE): str,
    vol.Optional(TASK_ID): int,
    vol.Optional(TASK_ITEM): [vol.Schema({
        vol.Required(TASK_NAME): str,
        vol.Required(TASK_POSITION): int,
        vol.Optional(TASK_DONE): bool,
    })]
})

TASK_UPDATE_SCHEMA = vol.Schema({
    vol.Required(TASK_NAME): vol.All(cv.string, vol.Length(min=1)),
    vol.Required(TASK_LIST_ID): str,
    vol.Required(TASK_DONE): bool,
    vol.Optional(TASK_DESCRIPTION): str,
    vol.Optional(TASK_DUE_DATE): str,
    vol.Required(TASK_ID): int,
    vol.Optional(TASK_ITEM): [vol.Schema({
        vol.Required(TASK_NAME): str,
        vol.Required(TASK_POSITION): int,
        vol.Optional(TASK_DONE): bool,
    })]
})

TASK_DELETE_SCHEMA = vol.Schema({
    vol.Required(TASK_LIST_ID): str,
    vol.Required(TASK_ID): int,
})

PERSISTENCE = ".task_list.json"


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""
    task_list = TaskList(hass, config_entry.entry_id, config_entry.data["name"],
                         config_entry.data["user"] if "user" in config_entry.data else None)
    hass.data[DOMAIN][config_entry.entry_id] = task_list
    async_add_devices([task_list])


class TaskList(Entity):
    def __init__(self, hass, id, name, user):
        """Init dummy roller."""
        self.hass = hass
        self._id = id
        self._name = name
        self._user = user
        self.entity_id = generate_entity_id("sensor." + DOMAIN + "_{}", self._id, hass=hass)
        self._tasks = []
        self.load_task()

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return f"task_list_{self._id}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return len(self._tasks)

    @property
    def unit_of_measurement(self):
        return "Task(n)"

    @property
    def state_attributes(self) -> dict:
        """Return optional state attributes."""
        return {ATTR_TASKS: [item.to_map() for item in self._tasks]}

    def add_task(self, conf):
        current_id = max([i.id for i in self._tasks], default=0)
        conf[TASK_ID] = current_id + 1
        self._tasks.append(Task(conf, self._id))
        self.save_task()

    def update_task(self, conf):
        task_id = conf[TASK_ID]
        for task in filter(lambda x: x.id == task_id, self._tasks):
            task.update(conf)

        self.save_task()

    def delete_task(self, conf):
        task_id = conf[TASK_ID]
        for task in filter(lambda x: x.id == task_id, self._tasks):
            self._tasks.remove(task)
        self.save_task()

    def delete_task_items(self, task_id):
        for task in filter(lambda x: x.id == task_id, self._tasks):
            task.remove_done_item()
        self.save_task()
        
    def save_task(self):
        save_json(self.hass.config.path(PERSISTENCE + "_" + self._name), [item.to_map() for item in self._tasks])

        asyncio.run_coroutine_threadsafe(entity_component.async_update_entity(self.hass, self.entity_id), self.hass.loop)

    def load_task(self):
        self._tasks = [Task(conf, self._id) for conf in load_json(self.hass.config.path(PERSISTENCE + "_" + self._name), [])]


class Task:
    id: int = None
    name: str = None
    description: str = None
    due_date: str = None
    done: bool = None
    done_timestamp: str = None
    item: list = None

    def __init__(self, conf, task_list_id):
        self.update(conf)
        self.task_list_id = task_list_id

    def update(self, conf):
        self.id = conf.get(TASK_ID, "")
        self.name = conf.get(TASK_NAME, "")
        self.description = conf.get(TASK_DESCRIPTION, "")
        self.due_date = conf.get(TASK_DUE_DATE, "")
        self.done = conf.get(TASK_DONE, False)
        self.item = [TaskItem(item) for item in conf.get(TASK_ITEM, [])]
        self.item.sort(key=lambda task_item: task_item.position)
        i = 1
        for item in self.item:
            item.position = i
            i += 1

    def remove_done_item(self):
        remove = list(filter(lambda x: x.done is True, self.item))
        for task in remove:
            self.item.remove(task)

    def to_map(self):
        return {
            TASK_NAME: self.name,
            TASK_LIST_ID: self.task_list_id,
            TASK_DESCRIPTION: self.description,
            TASK_DUE_DATE: self.due_date,
            TASK_DONE: self.done,
            TASK_ID: self.id,
            TASK_ITEM: [item.to_map() for item in self.item]
        }


class TaskItem:
    position: int = None
    name: str = None
    done: bool = None

    def __init__(self, conf):
        self.position = conf.get(TASK_POSITION)
        self.name = conf.get(TASK_NAME)
        self.done = conf.get(TASK_DONE, False)

    def to_map(self):
        return {
            TASK_NAME: self.name,
            TASK_DONE: self.done,
            TASK_POSITION: self.position,
        }
