"""Element class"""
import logging
from homeassistant.helpers.restore_state import RestoreEntity
from .const import DOMAIN_DATA

_LOGGER = logging.getLogger(__name__)


class Element(RestoreEntity):
    """Element Class"""
    def __init__(self, hass, name):
        """Set up an element."""
        self.hass = hass
        self.data = hass.data[DOMAIN_DATA].get(name, {})
        self._name = name
        self._state = None

    async def async_update(self):
        """Update entity"""
        _LOGGER.info('Updating %s', self._name)
        self.data = self.hass.data[DOMAIN_DATA].get(self._name, {})
        await self.get_state_value()  # Update state

    async def get_state_value(self):
        """Get state value"""
        if self.restart_pending:
            self._state = 'Restart pending'
        elif self.avaiable_version != self.installed_version:
            self._state = 'Update pending'
        else:
            self._state = 'Tracking'

    @property
    def unique_id(self):
        """Return a unique ID for the element."""
        return self._name

    @property
    def name(self):
        """Return the name of the entity."""
        return self._name

    @property
    def should_poll(self):
        """Return True if entity has to be polled for state"""
        return True

    @property
    def element_type(self):
        """element_type."""
        return self.data.get('element_type')

    @property
    def restart_pending(self):
        """restart_pending."""
        return self.data.get('restart_pending', False)

    @property
    def installed_version(self):
        """installed_version."""
        return self.data.get('installed_version')

    @property
    def avaiable_version(self):
        """avaiable_version."""
        return self.data.get('avaiable_version')

    @property
    def state(self):
        """Return the state of the element."""
        return self._state

    @property
    def icon(self):
        """Return the icon of the element."""
        return 'mdi:package-variant'

    @property
    def state_attributes(self):
        """Return the state attributes of the element."""
        return self.hass.data[DOMAIN_DATA].get('remote', {}).get(self._name, {})
