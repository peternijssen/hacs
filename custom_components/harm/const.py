"""Constants for HARM"""
VERSION = '1.0.0'
NAME_LONG = "HARM (Home Assistant Resource Manager)"
NAME_SHORT = "HARM"
PROJECT_URL = 'https://github.com/ludeeus/harm/'
CUSTOM_UPDATER_DIR = "{}/custom_components/custom_updater.py"
ISSUE_URL = "{}issues".format(PROJECT_URL)
DOMAIN_DATA = "{}_data".format(NAME_SHORT.lower())
ELEMENT_TYPES = ['card', 'component', 'python_script']



















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