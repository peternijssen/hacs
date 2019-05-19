"""
Resource manager for community created resources.

For more details about this component, please refer to the documentation at
https://github.com/custom-components/hacs
"""
import logging
import os.path
import json
import asyncio
import functools
from datetime import timedelta
from homeassistant.const import EVENT_HOMEASSISTANT_START
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.event import async_track_time_interval
from . const import (
    CUSTOM_UPDATER_DIR, STARTUP, PROJECT_URL, ISSUE_URL,
    CUSTOM_UPDATER_WARNING, NAME_LONG, NAME_SHORT, DOMAIN_DATA,
    ELEMENT_TYPES, VERSION, IFRAME, SKIP)
from .element import Element
from .data import get_data_from_store, write_to_data_store
from .files.overview import CommunityOverview, CommunityElementView, CommunityStoreView, CommunitySettingsView, CommunityAPI


DOMAIN = '{}'.format(NAME_SHORT.lower())

INTERVAL = timedelta(minutes=5)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):  # pylint: disable=unused-argument
    """Set up this component."""
    msg = STARTUP.format(name=NAME_LONG, version=VERSION, issueurl=ISSUE_URL)
    _LOGGER.info(msg)
    config_dir = hass.config.path()
    github_token = "7b69517f6eb44c879accb2c7f19b85ea32a26f7f"
    commander = HacsCommander(hass, github_token)

    if os.path.exists(CUSTOM_UPDATER_DIR.format(config_dir)):
        msg = CUSTOM_UPDATER_WARNING.format(
            CUSTOM_UPDATER_DIR.format(config_dir))
        _LOGGER.critical(msg)
        #return False

    # Setup background tasks
    hass.bus.async_listen_once(
        EVENT_HOMEASSISTANT_START, commander.startup_tasks())

    # Register the views
    hass.http.register_view(CommunityOverview(hass))
    hass.http.register_view(CommunityElementView(hass))
    hass.http.register_view(CommunityStoreView(hass))
    hass.http.register_view(CommunitySettingsView(hass))
    hass.http.register_view(CommunityAPI(hass))


    hass.data[DOMAIN_DATA] = {}
    hass.data[DOMAIN_DATA]['commander'] = commander

    # Add to sidepanel
    await hass.components.frontend.async_register_built_in_panel(
                'iframe', IFRAME['title'], IFRAME['icon'],
                IFRAME['path'], {'url': IFRAME['url']},
                require_admin=IFRAME['require_admin'])

    # Mischief managed!
    return True


class HacsCommander:

    def __init__(self, hass, github_token):
        """Initialize HacsCommander"""
        import github
        self.hass = hass
        self.git = github.Github(github_token)
        self.skip = SKIP

    async def load_integrations_from_git(self, repo_name):
        """Load data from repo."""
        _LOGGER.debug(repo_name)
        if repo_name in self.skip:
            return
        _LOGGER.debug("Loading from GIT")
        exists = False
        releases = []
        try:
            repo = self.git.get_repo(repo_name)
        except Exception as error:
            _LOGGER.error(error)
            self.skip.append(repo_name)
            return

        _LOGGER.debug("Got repo")

        # Find releases
        try:
            releases = list(repo.get_releases())
        except Exception as error:
            _LOGGER.debug(error)

        if not releases:
            _LOGGER.error("No releases found!")
            self.skip.append(repo_name)
            return

        ref = "tags/{}".format(list(repo.get_releases())[0].tag_name)

        # Find component location
        try:
            compdir = repo.get_dir_contents('custom_components', ref)[0].path
            dir = repo.get_dir_contents(compdir, ref)
            content = []
            for item in list(dir):
                content.append(item.path)
            _LOGGER.debug(content)
            manifest_path = "{}/manifest.json".format(compdir)
            if manifest_path in content:
                exists = True

                manifest = repo.get_file_contents(manifest_path, ref)
        except Exception as error:
            _LOGGER.debug(error)

        if not exists:
            _LOGGER.error("Can't get data from %s", repo_name)
            self.skip.append(repo_name)
            return

        # Load manifest
        try:
            manifest = json.loads(manifest.decoded_content.decode())
            _LOGGER.critical(manifest)
        except Exception as error:
            _LOGGER.debug(error)
            return


        # Check manifest
        if len(manifest['domain'].split()) > 1:
            _LOGGER.debug("Manifest not valid")
            return
        elif "http" in manifest['domain']:
            _LOGGER.debug("Manifest not valid")
            return

        # Now we can trust this repo.

        # Load existing Element object.
        if manifest['domain'] in self.hass.data[DOMAIN_DATA]['elements']:
            element = self.hass.data[DOMAIN_DATA]['elements'][manifest['domain']]
        else:
            element = Element('integration', manifest['domain'])

        # Get example config
        try:
            example = repo.get_file_contents('example.yaml', ref).decoded_content.decode()
            element.example_config = example
        except Exception as error:
            _LOGGER.debug(error)

        # Get example image
        try:
            element.example_image = repo.get_file_contents('example.png').download_url
        except Exception as error:
            _LOGGER.debug(error)

        element.name = manifest['name']
        element.avaiable_version = list(repo.get_releases())[0].tag_name
        element.description = repo.description
        element.repo = repo_name


        # Save it back to hass.data
        self.hass.data[DOMAIN_DATA]['elements'][manifest['domain']] = element

    async def load_plugins_from_git(self, repo_name):
        """Load data from repo."""
        _LOGGER.debug(repo_name)
        if repo_name in self.skip:
            return
        _LOGGER.debug("Loading from GIT")
        exists = True
        releases = []
        try:
            repo = self.git.get_repo(repo_name)
        except Exception as error:
            _LOGGER.error(error)
            self.skip.append(repo_name)
            return

        _LOGGER.debug("Got repo")

        name = repo_name.split('/')[-1]

        # Find releases
        try:
            releases = list(repo.get_releases())
        except Exception as error:
            _LOGGER.debug(error)

        if not releases:
            _LOGGER.error("No releases found!")
            self.skip.append(repo_name)
            return

        ref = "tags/{}".format(list(repo.get_releases())[0].tag_name)

        if not exists:
            _LOGGER.error("Can't get data from %s", repo_name)
            self.skip.append(repo_name)
            return

        # Now we can trust this repo.

        # Load existing Element object.
        if name in self.hass.data[DOMAIN_DATA]['elements']:
            element = self.hass.data[DOMAIN_DATA]['elements'][name]
        else:
            element = Element('plugin', name)

        element.name = name
        element.avaiable_version = list(repo.get_releases())[0].tag_name
        element.description = repo.description
        element.repo = repo_name

        # Get example config
        try:
            example = repo.get_file_contents('example.yaml').decoded_content.decode()
            element.example_config = example
        except Exception as error:
            _LOGGER.debug(error)

        # Save it back to hass.data
        self.hass.data[DOMAIN_DATA]['elements'][name] = element

    async def background_tasks(self, runas=None):
        """Run background_tasks."""
        _LOGGER.debug("Run background_tasks.")

        # Check HACS
        try:
            hacs = self.git.get_repo("custom-components/hacs")
            self.hass.data[DOMAIN_DATA]['hacs']['remote'] = list(hacs.get_releases())[0].tag_name
        except Exception as error:
            _LOGGER.error(error)

        integration_repos = []
        plugin_repos = []

        for repo in list(self.git.get_organization("custom-components").get_repos()):
            if repo.archived:
                continue
            if repo.full_name in self.skip:
                continue
            integration_repos.append(repo.full_name)

        if self.hass.data[DOMAIN_DATA]['repos'].get('integration'):
            for entry in self.hass.data[DOMAIN_DATA]['repos'].get('integration'):
                _LOGGER.debug("Checking custom repo %s", entry)
                repo = entry
                if "http" in repo:
                    repo = repo.split('https://github.com/')[-1]

                if len(repo.split('/')) != 2:
                    _LOGGER.error("%s is not valid", entry)
                    continue

                try:
                    repo = self.git.get_repo(repo)
                    if not repo.archived or repo.full_name not in self.skip:
                        integration_repos.append(repo.full_name)
                except Exception as error:
                    _LOGGER.error(error)

        for repo in list(self.git.get_organization("custom-cards").get_repos()):
            if repo.archived:
                continue
            if repo.full_name in self.skip:
                continue
            plugin_repos.append(repo.full_name)

        if self.hass.data[DOMAIN_DATA]['repos'].get('plugin'):
            for entry in self.hass.data[DOMAIN_DATA]['repos'].get('plugin'):
                _LOGGER.debug("Checking custom repo %s", entry)
                repo = entry
                if "http" in repo:
                    repo = repo.split('https://github.com/')[-1]

                if len(repo.split('/')) != 2:
                    _LOGGER.error("%s is not valid", entry)
                    continue

                try:
                    repo = self.git.get_repo(repo)
                    if not repo.archived or repo.full_name not in self.skip:
                        plugin_repos.append(repo.full_name)
                except Exception as error:
                    _LOGGER.error(error)

        _LOGGER.debug(integration_repos)

        for repo in integration_repos:
            await self.load_integrations_from_git(repo)

        _LOGGER.debug(plugin_repos)

        for repo in plugin_repos:
            await self.load_plugins_from_git(repo)

        await write_to_data_store(self.hass.config.path(), self.hass.data[DOMAIN_DATA])

    async def startup_tasks(self):
        """Run startup_tasks."""
        _LOGGER.debug("Run startup_tasks.")
        async_track_time_interval(self.hass, self.background_tasks, INTERVAL)


        _LOGGER.info("Loading existing data.")
        # Ready up hass.data
        returndata = await get_data_from_store(self.hass.config.path())
        if not returndata.get('elements'):
            self.hass.data[DOMAIN_DATA]['elements'] = {}
            self.hass.data[DOMAIN_DATA]['repos'] = {"integration": [], "plugin": []}
            self.hass.data[DOMAIN_DATA]['hacs'] = {"local": VERSION, "remote": None}
            await self.background_tasks()
        else:
            self.hass.data[DOMAIN_DATA]['elements'] = returndata['elements']
            self.hass.data[DOMAIN_DATA]['repos'] = returndata['repos']
            self.hass.data[DOMAIN_DATA]['hacs'] = returndata['hacs']
