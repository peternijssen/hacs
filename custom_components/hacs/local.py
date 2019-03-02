"""Local data."""
import logging

_LOGGER = logging.getLogger(__name__)


async def get_local_data(element_type):
    """Get local data."""
    return_value = {}

    async def cards():
        """Get local cards."""
        data = {}
        try:
            data = {}
        except:
            _LOGGER.error('Could not update data')
        return data

    async def components():
        """Get local components."""
        data = {}
        try:
            data = {}
        except:
            _LOGGER.error('Could not update data')
        return data

    if element_type == 'card':
        return_value = await cards()
    elif element_type == 'component':
        return_value = await components()
    else:
        _LOGGER.error('element_type %s is not valid', element_type)

    return return_value
