"""Remote data."""
import logging
import requests

_LOGGER = logging.getLogger(__name__)


async def get_remote_data(element_type):
    """Get remote data."""
    return_value = {}
    async def cards():
        """Get remote cards."""
        data = {}
        try:
            resp = requests.get('https://raw.githubusercontent.com/custom-components/information/master/repos.json').json()
            data = resp
        except:
            _LOGGER.error('Could not update data')
        return data
        
    async def components():
        """Get remote components."""
        data = {}
        try:
            resp = requests.get('https://raw.githubusercontent.com/custom-components/information/master/repos.json').json()
            data = resp
        except:
            _LOGGER.error('Could not update data')
        return data
        
    async def python_scripts():
        """Get remote python_scripts."""
        data = {}
        try:
            resp = requests.get('https://raw.githubusercontent.com/custom-components/information/master/repos.json').json()
            data = resp
        except:
            _LOGGER.error('Could not update data')
        return data
    
    if element_type == 'card':
        return_value = await cards()
    elif element_type == 'component':
        return_value = await components()
    elif element_type == 'python_script':
        return_value = await python_scripts()
    else:
        _LOGGER.error('element_type %s is not valid', element_type())

    return return_value