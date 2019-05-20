"""Update data."""
import logging
from custom_components.hacs.const import DOMAIN_DATA
from custom_components.hacs.handler.storage import write_to_data_store

_LOGGER = logging.getLogger(__name__)


async def update_data_after_action(hass, element):
    """
    Updates the data we have of the element after an action is completed.
    """

    # Update the data
    hass.data[DOMAIN_DATA]['elements'][element.element_id] = element

    # Save the data to storage.
    await write_to_data_store(hass.config.path(), hass.data[DOMAIN_DATA])
