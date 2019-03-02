"""
Resource manager for community created resources.

For more details about this component, please refer to the documentation at
https://github.com/custom-components/harm
"""
import logging
import os.path
from datetime import timedelta
import asyncio
import requests
import voluptuous as vol
from aiohttp import web
from homeassistant.const import EVENT_HOMEASSISTANT_START
from . const import CUSTOM_UPDATER_DIR, STARTUP, PROJECT_URL, ISSUE_URL, CUSTOM_UPDATER_WARNING, NAME_LONG, NAME_SHORT, DOMAIN_DATA, ELEMENT_TYPES, VERSION
import homeassistant.helpers.config_validation as cv
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.entity_component import EntityComponent
from .element import Element
from .remote import get_remote_data


DOMAIN = '{}'.format(NAME_SHORT.lower())

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Set up this component."""
    hass.data[DOMAIN_DATA] = {}
    _LOGGER.info(STARTUP.format(name=NAME_LONG, version=VERSION, issueurl=ISSUE_URL))
    config_dir = hass.config.path()

    if os.path.exists(CUSTOM_UPDATER_DIR.format(config_dir)):
        _LOGGER.error(CUSTOM_UPDATER_WARNING.format(CUSTOM_UPDATER_DIR.format(config_dir)))
        #return False

    hass.data[DOMAIN_DATA]['remote'] = await refresh_data(hass)
    return True


async def refresh_data(hass):
    """Refresh data."""
    data = {}
    for element_type in ELEMENT_TYPES:
        element_data = await get_remote_data(element_type)
        for element in element_data:
            data[element] = element_data[element]

    harm_data = hass.data.get(DOMAIN_DATA, {})
    tasks = []

    for element in data:
        if element not in harm_data:
            _LOGGER.info('Adding %s', element)
            tasks.append(add_new_element(hass, element))

    if tasks:
        for task in asyncio.as_completed(tasks):
            await task

    return data


async def add_new_element(hass, name):
    """Add new element to Home Assistant."""
    component = EntityComponent(_LOGGER, DOMAIN, hass)
    await component.async_add_entities([Element(hass, name)])
    hass.data[DOMAIN_DATA][name] = {}