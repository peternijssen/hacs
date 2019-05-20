"""Local data handling."""
import logging
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import async_timeout
import json
import os
import asyncio
import shutil
from .const import STORENAME, DOMAIN_DATA, VERSION
from .element import Element

_LOGGER = logging.getLogger(__name__)

async def get_data_from_store(basedir):
    """Get data from element store."""
    datastore = "{}/.storage/{}".format(basedir, STORENAME)
    elements = {}
    returndata = {}
    try:
        with open(datastore, encoding='utf-8', errors='ignore') as localfile:
            data = json.load(localfile)
            localfile.close()
        returndata['repos'] = {}
        returndata['repos']['integration'] = data['repos'].get('integration', [])
        returndata['repos']['plugin'] = data['repos'].get('plugin', [])
        returndata['hacs'] = data.get('hacs', {"local": VERSION, "remote": None})
        for element in data['elements']:
            edata = Element(data['elements'][element]['element_type'], element)
            for entry in data['elements'][element]:
                edata.__setattr__(entry, data['elements'][element][entry])
            edata.__setattr__('restart_pending', False)
            elements[element] = edata
        returndata['elements'] = elements
    except Exception as error:  # pylint: disable=W0703
        msg = "Could not load data from {} - {}".format(datastore, error)
        _LOGGER.debug(msg)
    return returndata


async def write_to_data_store(basedir, output):
    """Get data from element store."""
    _LOGGER.debug("Writing to datastore.")
    datastore = "{}/.storage/{}".format(basedir, STORENAME)
    outdata = {}
    outdata['hacs'] = output['hacs']
    outdata['repos'] = output['repos']
    outdata['elements'] = {}
    for element in output['elements']:
        edata = {}
        for attribute, value in output['elements'][element].__dict__.items():
            edata[attribute] = value
        outdata['elements'][output['elements'][element].element_id] = edata
    try:
        with open(datastore, 'w', encoding='utf-8', errors='ignore') as outfile:
            json.dump(outdata, outfile, indent=4)
            outfile.close()
    except Exception as error:  # pylint: disable=W0703
        msg = "Could not write data to {} - {}".format(datastore, error)
        _LOGGER.debug(msg)

async def remove_plugin(hass, plugin):
    """Remove integration"""
    plugindir = "{}/www/community/{}".format(hass.config.path(), plugin.element_id)
    if os.path.exists(plugindir):
        shutil.rmtree(plugindir)
        while os.path.exists(plugindir):
            _LOGGER.debug("%s still exist, waiting 1s and checking again.", plugindir)
            await asyncio.sleep(1)

    # Update hass.data
    plugin.installed_version = None
    plugin.isinstalled = False
    plugin.restart_pending = True
    hass.data[DOMAIN_DATA]['elements'][plugin.element_id] = plugin

async def remove_integration(hass, integration):
    """Remove integration"""
    integrationdir = "{}/custom_components/{}".format(hass.config.path(), integration.element_id)
    if os.path.exists(integrationdir):
        shutil.rmtree(integrationdir)
        while os.path.exists(integrationdir):
            _LOGGER.debug("%s still exist, waiting 1s and checking again.", integrationdir)
            await asyncio.sleep(1)

    # Update hass.data
    integration.installed_version = None
    integration.isinstalled = False
    integration.restart_pending = True
    hass.data[DOMAIN_DATA]['elements'][integration.element_id] = integration

async def download_plugin(hass, plugin):
    """Download plugin"""
    commander = hass.data[DOMAIN_DATA]['commander']
    git = commander.git
    pluginbasedir = "{}/www/community".format(hass.config.path())
    if not os.path.exists(pluginbasedir):
        os.mkdir(pluginbasedir)
    plugindir = "{}/{}".format(pluginbasedir, plugin.element_id)
    try:
        if os.path.exists(plugindir):
            _LOGGER.debug("%s exist, deleting current content before download.", plugindir)
            await remove_plugin(hass, plugin)
        os.mkdir(plugindir)
        repo = git.get_repo(plugin.repo)
        ref = "tags/{}".format(plugin.avaiable_version)

        # Try dist
        try:
            remotedir = repo.get_dir_contents("dist", ref)
        except Exception as error:
            _LOGGER.debug(error)

        # Try root
        try:
            remotedir = repo.get_dir_contents("", ref)
        except Exception as error:
            _LOGGER.debug(error)

        _LOGGER.debug(str(list(remotedir)))
        for file in remotedir:
            if not file.name.endswith('.js'):
                continue
            _LOGGER.debug("Downloading %s", file.path)
            filecontent = await async_download_file(hass, file.download_url)
            if filecontent is None:
                _LOGGER.error("There was an error downloading the file.")
                return
            local_file_path = "{}/{}".format(plugindir, file.name)
            with open(local_file_path, 'w', encoding='utf-8', errors='ignore') as outfile:
                outfile.write(filecontent)
                outfile.close()

        # Update hass.data
        plugin.installed_version = plugin.avaiable_version
        plugin.isinstalled = True
        plugin.restart_pending = True
        hass.data[DOMAIN_DATA]['elements'][plugin.element_id] = plugin
        await write_to_data_store(hass.config.path(), hass.data[DOMAIN_DATA])

    except Exception as error:
        _LOGGER.error(error)

async def download_integration(hass, integration):
    """Download integration"""
    commander = hass.data[DOMAIN_DATA]['commander']
    git = commander.git
    integrationdir = "{}/custom_components/{}".format(hass.config.path(), integration.element_id)
    try:
        if os.path.exists(integrationdir):
            _LOGGER.debug("%s exist, deleting current content before download.", integrationdir)
            await remove_integration(hass, integration)
        os.mkdir(integrationdir)
        repo = git.get_repo(integration.repo)
        ref = "tags/{}".format(integration.avaiable_version)
        remotedir = repo.get_dir_contents(repo.get_dir_contents("custom_components", ref)[0].path)
        _LOGGER.debug(str(list(remotedir)))
        for file in remotedir:
            _LOGGER.debug("Downloading %s", file.path)
            filecontent = await async_download_file(hass, file.download_url)
            if filecontent is None:
                _LOGGER.error("There was an error downloading the file.")
                return
            local_file_path = "{}/{}".format(integrationdir, file.name)
            with open(local_file_path, 'w', encoding='utf-8', errors='ignore') as outfile:
                outfile.write(filecontent)
                outfile.close()

        # Update hass.data
        integration.installed_version = integration.avaiable_version
        integration.isinstalled = True
        integration.restart_pending = True
        hass.data[DOMAIN_DATA]['elements'][integration.element_id] = integration
        await write_to_data_store(hass.config.path(), hass.data[DOMAIN_DATA])

    except Exception as error:
        _LOGGER.error(error)


async def download_hacs(hass):
    """Download hacs"""
    commander = hass.data[DOMAIN_DATA]['commander']
    git = commander.git
    integrationdir = "{}/custom_components/hacs".format(hass.config.path())
    try:
        if os.path.exists(integrationdir):
            _LOGGER.debug("%s exist, deleting current content before download.", integrationdir)
            shutil.rmtree(integrationdir)
            while os.path.exists(integrationdir):
                _LOGGER.debug("%s still exist, waiting 1s and checking again.", integrationdir)
        os.mkdir(integrationdir)
        os.mkdir("{}/flies".format(integrationdir))
        repo = git.get_repo("custom-components/hacs")
        ref = "tags/{}".format(hass.data[DOMAIN_DATA]['hacs']['remote'])
        remotedir = repo.get_dir_contents("custom_components/hacs", ref)
        _LOGGER.debug(str(list(remotedir)))
        for file in remotedir:
            if file == "files":
                continue
            _LOGGER.debug("Downloading %s", file.path)
            filecontent = await async_download_file(hass, file.download_url)
            if filecontent is None:
                _LOGGER.error("There was an error downloading the file.")
                return
            local_file_path = "{}/{}".format(integrationdir, file.name)
            with open(local_file_path, 'w', encoding='utf-8', errors='ignore') as outfile:
                outfile.write(filecontent)
                outfile.close()
        remotedir = repo.get_dir_contents("custom_components/hacs/files", ref)
        _LOGGER.debug(str(list(remotedir)))
        for file in remotedir:
            _LOGGER.debug("Downloading %s", file.path)
            filecontent = await async_download_file(hass, file.download_url)
            local_file_path = "{}/{}".format(integrationdir, file.name)
            with open(local_file_path, 'w', encoding='utf-8', errors='ignore') as outfile:
                outfile.write(filecontent)
                outfile.close()

        # Update hass.data
        hass.data[DOMAIN_DATA]['hacs']['local'] = hass.data[DOMAIN_DATA]['hacs']['remote']
        hass.data[DOMAIN_DATA]['hacs']['restart_pending'] = True
        await write_to_data_store(hass.config.path(), hass.data[DOMAIN_DATA])

    except Exception as error:
        _LOGGER.error(error)


async def async_download_file(hass, url):
    """Download files."""
    _LOGGER.debug("Donwloading from %s", url)
    if "tags/" in url:
        url = url.replace("tags/", "")
    result = None
    with async_timeout.timeout(10, loop=hass.loop):
        request = await async_get_clientsession(hass).get(url)
        if request.status == 200:
            result = await request.text()
    return result
