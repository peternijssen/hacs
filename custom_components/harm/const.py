"""Constants for HACS"""
VERSION = '1.0.0'
NAME_LONG = "HACS (Home Assistant Community Store)"
NAME_SHORT = "HACS"
PROJECT_URL = 'https://github.com/ludeeus/hacs/'
CUSTOM_UPDATER_DIR = "{}/custom_components/custom_updater.py"
ISSUE_URL = "{}issues".format(PROJECT_URL)
DOMAIN_DATA = "{}_data".format(NAME_SHORT.lower())
GHRAW = 'https://raw.githubusercontent.com/'
ELEMENT_TYPES = ['card', 'component']
REPO = {'card': 'custom-cards/information/master/repos.json',
        'component': 'custom-components/information/master/repos.json'}



















# Messages
CUSTOM_UPDATER_WARNING = """
This cannot be used with custom_updater.
To use this you need to remove custom_updater form {}
"""

STARTUP = """
----------------------------------------------
{name}
Version: {version}
This is a custom component, if you have any issues with this you need to open an issue here:
{issueurl}
----------------------------------------------
"""