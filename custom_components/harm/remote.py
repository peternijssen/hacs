"""Remote data."""
import logging
import requests
from .const import GHRAW, REPO

_LOGGER = logging.getLogger(__name__)


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
        except:
            _LOGGER.error('Could not update data from %s', repo)
        return data

    async def components():
        """Get remote components."""
        data = {}
        try:
            repo = "{}{}".format(GHRAW, REPO['component'])
            resp = requests.get(repo).json()
            data = resp
        except:
            _LOGGER.error('Could not update data from %s', repo)
        return data


    if element_type == 'card':
        return_value = await cards()
    elif element_type == 'component':
        return_value = await components()
    else:
        _LOGGER.error('element_type %s is not valid', element_type)

    return return_value
