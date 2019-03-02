"""Local data handling."""
import os
from .cons import NAME_SHORT, ELEMENT_TYPES


async def init_data_store(basedir):
    """Init data store."""
    name = NAME_SHORT.lower()
    data_stores = []
    for element in ELEMENT_TYPES:
        data_stores.append("{}.{}".format(name, element))
    for data_store in data_stores:
        fullpath = "{}/.storage/{}".format(basedir, data_store)
        if not os.path.exists(fullpath):
            print('Create dummyfiles here.')


async def get_data_from_store(basedir, element_type, element):
    """Get data from element store."""
    data = {}
    return data
