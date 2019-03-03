"""
Resource manager for community created resources.

For more details about this component, please refer to the documentation at
https://github.com/custom-components/hacs
"""
import logging
import os.path
import asyncio
from homeassistant.helpers.entity_component import EntityComponent
from . const import (
    CUSTOM_UPDATER_DIR, STARTUP, PROJECT_URL, ISSUE_URL,
    CUSTOM_UPDATER_WARNING, NAME_LONG, NAME_SHORT, DOMAIN_DATA,
    ELEMENT_TYPES, VERSION)
from .element import Element
from .data import (
    get_remote_data, get_data_from_store, get_local_data, write_to_data_store)


DOMAIN = '{}'.format(NAME_SHORT.lower())

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):  # pylint: disable=unused-argument
    """Set up this component."""
    hass.data[DOMAIN_DATA] = {}
    msg = STARTUP.format(name=NAME_LONG, version=VERSION, issueurl=ISSUE_URL)
    _LOGGER.info(msg)
    config_dir = hass.config.path()

    if os.path.exists(CUSTOM_UPDATER_DIR.format(config_dir)):
        msg = CUSTOM_UPDATER_WARNING.format(
            CUSTOM_UPDATER_DIR.format(config_dir))
        _LOGGER.error(msg)
        #return False

    async def reload_service(call):  # pylint: disable=unused-argument
        """Reload remote and stored data."""
        _LOGGER.info("Reloading remote and stored data")
        await refresh_data(hass)

    hass.services.async_register(DOMAIN, 'reload', reload_service)
    await startup_background_tasks(hass)
    return True


async def refresh_data(hass, runtype=None):  # pylint: disable=unused-argument
    """Refresh data."""
    config_dir = hass.config.path()
    tasks = []
    async def refresh_remote_data():
        """Refresh remote data."""
        hass.data[DOMAIN_DATA]['remote'] = {}
        for element_type in ELEMENT_TYPES:
            elementdata = await get_remote_data(element_type)
            hass.data[DOMAIN_DATA]['remote'][element_type] = elementdata

    async def refresh_stored_data():
        """Refresh stored data."""
        for element_type in ELEMENT_TYPES:
            stored_data = await get_data_from_store(config_dir, element_type)
            for element in stored_data:
                hass.data[DOMAIN_DATA][element] = stored_data[element]

    tasks.append(refresh_remote_data())
    tasks.append(refresh_stored_data())

    for task in asyncio.as_completed(tasks):
        await task


async def add_new_element(hass, name, hacs_data):
    """Add new element to Home Assistant."""
    component = EntityComponent(_LOGGER, DOMAIN, hass)
    hass.data[DOMAIN_DATA][name] = hacs_data
    await component.async_add_entities([Element(hass, name)], True)


async def startup_background_tasks(hass):
    """Run background_tasks."""
    tasks = []
    tasks.append(refresh_data(hass))
    for element_type in ELEMENT_TYPES:
        remotedata = await get_remote_data(element_type)
        localdata = await get_local_data(element_type)
        storeddata = await get_data_from_store(
            hass.config.path(), element_type)
        for element in remotedata:
            if element in localdata:
                if element in storeddata:
                    elementdata = storeddata[element]
                else:
                    elementdata = {}
                tasks.append(add_new_element(hass, element, elementdata))
                elementdata = {'restart_pending': False}
                tasks.append(
                    write_to_data_store(
                        hass.config.path(), element_type, element,
                        elementdata))

    for task in asyncio.as_completed(tasks):
        await task
