"""Local data handling."""
import os
import logging
import json
import requests
from .const import GHRAW, REPO, NAME_SHORT

_LOGGER = logging.getLogger(__name__)


async def init_data_store(datafile):
    """Init data store."""
    if not os.path.exists(datafile):
        try:
            with open(
                datafile, 'w', encoding='utf-8', errors='ignore') as outfile:
                json.dump({}, outfile, indent=4)
                outfile.close()
        except Exception as error:  # pylint: disable=W0703
            msg = "Could crate file {} - {}".format(datafile, error)
            _LOGGER.error(msg)
            return False
    return True


async def get_data_from_store(basedir, element_type, element=None):
    """Get data from element store."""
    name = NAME_SHORT.lower()
    datafile = "{}.{}".format(name, element_type)
    datafile = "{}/.storage/{}".format(basedir, datafile)
    exist = await init_data_store(datafile)
    data = {}
    if not exist:
        return data
    try:
        with open(datafile, encoding='utf-8', errors='ignore') as localfile:
            load = json.load(localfile)
            if element:
                data = load[element]
            else:
                data = load
            localfile.close()
    except Exception as error:  # pylint: disable=W0703
        msg = "Could not load data from {} - {}".format(datafile, error)
        _LOGGER.error(msg)
    return data


async def write_to_data_store(basedir, element_type, element, elementdata):
    """Get data from element store."""
    name = NAME_SHORT.lower()
    datafile = "{}.{}".format(name, element_type)
    datafile = "{}/.storage/{}".format(basedir, datafile)
    data = await get_data_from_store(basedir, element_type)
    if not element in data:
        data[element] = {}
        data[element]['element_type'] = element_type
    for key in elementdata:
        data[element][key] = elementdata[key]
    try:
        with open(datafile, 'w', encoding='utf-8', errors='ignore') as outfile:
            json.dump(data, outfile, indent=4)
            outfile.close()
    except Exception as error:  # pylint: disable=W0703
        msg = "Could not write data to {} - {}".format(datafile, error)
        _LOGGER.error(msg)


async def get_remote_data(element_type):
    """Get remote data."""
    return_value = {}
    async def cards():
        """Get remote cards."""
        data = {}
        try:
            repo = "{}{}".format(GHRAW, REPO['card'])
            resp = requests.get(repo).json()
            data = resp
        except Exception as error:  # pylint: disable=W0703
            msg = "Could not load data from {} - {}".format(repo, error)
            _LOGGER.error(msg)
        return data

    async def components():
        """Get remote components."""
        data = {}
        try:
            repo = "{}{}".format(GHRAW, REPO['component'])
            resp = requests.get(repo).json()
            data = resp
        except Exception as error:  # pylint: disable=W0703
            msg = "Could not load data from {} - {}".format(repo, error)
            _LOGGER.error(msg)
        return data


    if element_type == 'card':
        return_value = await cards()
    elif element_type == 'component':
        return_value = await components()
    else:
        _LOGGER.error('element_type %s is not valid', element_type)

    return return_value


async def get_local_data(element_type):
    """Get local data."""
    return_value = {}

    async def cards():
        """Get local cards."""
        data = {}
        try:
            data = {}
        except Exception as error:  # pylint: disable=W0703
            msg = "Could not load data - {}".format(error)
            _LOGGER.error(msg)
        return data

    async def components():
        """Get local components."""
        data = {}
        try:
            data = {}
            data['custom_updater'] = {}
            data['sensor.youtube'] = {}
        except Exception as error:  # pylint: disable=W0703
            msg = "Could not load data from - {}".format(error)
            _LOGGER.error(msg)
        return data

    if element_type == 'card':
        return_value = await cards()
    elif element_type == 'component':
        return_value = await components()
    else:
        _LOGGER.error('element_type %s is not valid', element_type)

    return return_value
