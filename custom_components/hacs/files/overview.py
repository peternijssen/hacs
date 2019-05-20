"""Serve overview."""
import logging
import os.path
import sys
import traceback

from aiohttp import web

from homeassistant.components.http import HomeAssistantView

from ..const import DOMAIN_DATA, NO_ELEMENTS
from ..data import download_integration, remove_integration, write_to_data_store, download_plugin, download_hacs
from .ui_elements import css, ui_header, ui_overview_card, ui_element_view, button

_LOGGER = logging.getLogger(__name__)


class CommunityElementView(HomeAssistantView):
    """View to serve the overview."""

    requires_auth = False

    url = r"/community_element/{path}"
    name = "community_element"

    def __init__(self, hass):
        """Initialize overview."""
        self.hass = hass

    async def get(self, request, path):
        """View to serve the overview."""
        _LOGGER.info(path)
        try:
            html = await self.element_view(path)
        except Exception as error:
            _LOGGER.error(error)
            html = await error_view()
        return web.Response(body=html, content_type="text/html", charset="utf-8")

    async def element_view(self, element):
        """element_view."""
        content = ""
        content += await css()
        content += await ui_header()
        content += "<div class='container''>"
        content += await ui_element_view(self.hass.data[DOMAIN_DATA]['elements'][element])
        content += "</div>"
        return content

class CommunityStoreView(HomeAssistantView):
    """View to serve the overview."""

    requires_auth = False

    url = r"/community_store"
    name = "community_store"

    def __init__(self, hass):
        """Initialize overview."""
        self.hass = hass

    async def get(self, request):
        """View to serve the overview."""
        try:
            html = await self.store_view()
        except Exception as error:
            _LOGGER.error(error)
            html = await error_view()
        return web.Response(body=html, content_type="text/html", charset="utf-8")

    async def store_view(self):
        """element_view."""
        content = ""
        content += await css()
        content += await ui_header()
        content += """
        <script>
            function Search() {
            var input = document.getElementById("Search");
            var filter = input.value.toLowerCase();
            var nodes = document.getElementsByClassName('row');

            for (i = 0; i < nodes.length; i++) {
                if (nodes[i].innerText.toLowerCase().includes(filter)) {
                nodes[i].style.display = "block";
                } else {
                nodes[i].style.display = "none";
                }
            }
            }
        </script>
        """
        content += "<div class='container''>"
        content += '<input type="text" id="Search" onkeyup="Search()" placeholder="Please enter a search term.." title="Type in a name">'
        content += "<h5>CUSTOM INTEGRATIONS</h5>"
        content += await overview(self.hass, 'integration')
        content += "<h5>CUSTOM PLUGINS (LOVELACE)</h5>"
        content += await overview(self.hass, 'plugin')
        content += "</div>"
        return content

class CommunitySettingsView(HomeAssistantView):
    """View to serve the overview."""

    requires_auth = False

    url = r"/community_settings"
    name = "community_settings"

    def __init__(self, hass):
        """Initialize overview."""
        self.hass = hass

    async def get(self, request):
        """View to serve the overview."""
        try:
            html = await self.settings_view()
        except Exception as error:
            _LOGGER.error(error)
            html = await error_view()
        return web.Response(body=html, content_type="text/html", charset="utf-8")

    async def settings_view(self):
        """element_view."""
        content = ""
        content += await css()
        content += await ui_header()

        content += "<div class='container''>"

        if self.hass.data[DOMAIN_DATA]['hacs'].get('pending_restart'):
            content += """
                <div class="row">
                    <div class="col s12">
                    <div class="card-panel orange darken-4">
                        <span class="white-text">
                        You need to restart Home Assisant to start using the latest version of HACS.
                        </span>
                    </div>
                    </div>
                </div>
            """

        if self.hass.data[DOMAIN_DATA]['hacs']['local'] != self.hass.data[DOMAIN_DATA]['hacs']['remote']:
            content += """
                <div class="row">
                    <div class="col s12">
                    <div class="card  red darken-4">
                        <div class="card-content white-text">
                        <span class="card-title">UPDATE PENDING</span>
                        <p>There is an update pending for HACS!.</p>
                        </br>
                        <p>Current version: {}</p>
                        <p>Available version: {}</p>
                        </div>
                        <div class="card-action">
                        <a href="/community_api/hacs/upgrade"
                            onclick="document.getElementById('progressbar').style.display = 'block'">
                            UPGRADE</a>
                        </div>
                    </div>
                    </div>
                </div>
            """.format(self.hass.data[DOMAIN_DATA]['hacs']['local'], self.hass.data[DOMAIN_DATA]['hacs']['remote'])

        # Integration URL's
        content += """
        <div class="row">
                <ul class="collection with-header">
                    <li class="collection-header"><h5>CUSTOM INTEGRATION REPO'S</h5></li>
        """
        if self.hass.data[DOMAIN_DATA]['repos'].get('integration'):
            for entry in self.hass.data[DOMAIN_DATA]['repos'].get('integration'):
                content += """
                    <li class="collection-item">
                        <div>{}
                            <a href="/community_api/integration_url_delete/{}" class="secondary-content">
                                <i name="delete" class="fas fa-trash-alt"></i>
                            </a>
                        </div>
                    </li>
                """.format(entry, entry.replace('/', '%2F'))
        content += """
                </ul>
            <form action="/community_api/integration_url/add" method="get">
                <input type="text" name="custom_url" placeholder="ADD CUSTOM INTEGRATION REPO" style="width: 90%">
                <input type="submit" value="ADD" style="margin-left: 2%">
            </form> 
            </br>
        """

        # Plugin URL's
        content += """
                <ul class="collection with-header">
                    <li class="collection-header"><h5>CUSTOM PLUGIN REPO'S</h5></li>
        """
        if self.hass.data[DOMAIN_DATA]['repos'].get('plugin'):
            for entry in self.hass.data[DOMAIN_DATA]['repos'].get('plugin'):
                content += """
                    <li class="collection-item">
                        <div>{}
                            <a href="/community_api/plugin_url_delete/{}" class="secondary-content">
                                <i name="delete" class="fas fa-trash-alt"></i>
                            </a>
                        </div>
                    </li>
                """.format(entry, entry.replace('/', '%2F'))
        content += """
                </ul>
            <form action="/community_api/plugin_url/add" method="get">
                <input type="text" name="custom_url" placeholder="ADD CUSTOM PLUGIN REPO" style="width: 90%">
                <input type="submit" value="ADD" style="margin-left: 2%">
            </form> 
        </div>
        """

        # Reload button
        content += "</br>"
        content += "</br>"
        content += "</br>"
        content += await button('/community_api/self/reload', 'RELOAD DATA')
        content += """
            <a href='https://github.com/custom-components/hacs/issues/new'
                class='waves-effect waves-light btn'
                target="_blank" style="float: right">
                OPEN ISSUE
            </a>
        """
        content += "</div>"
        return content


class CommunityAPI(HomeAssistantView):
    """View to serve the overview."""

    requires_auth = False

    url = r"/community_api/{element}/{action}"
    name = "community_api"

    def __init__(self, hass):
        """Initialize overview."""
        self.hass = hass

    async def get(self, request, element, action):
        """View to serve the overview."""
        _LOGGER.debug("API call for %s with %s", element, action)
        if action == 'reload':
            await self.hass.data[DOMAIN_DATA]['commander'].background_tasks()
            raise web.HTTPFound('/community_settings')

        elif element == 'hacs' and action == 'upgrade':
            await download_hacs(self.hass)
            raise web.HTTPFound('/community_settings')

        elif action in ['install', 'upgrade']:
            element = self.hass.data[DOMAIN_DATA]['elements'][element]
            if element.element_type == 'integration':
                await download_integration(self.hass, element)
            elif element.element_type == 'plugin':
                await download_plugin(self.hass, element)
            raise web.HTTPFound('/community_element/' + element.element_id)

        elif element == 'integration_url_delete':
            self.hass.data[DOMAIN_DATA]['repos']['integration'].remove(action)
            await write_to_data_store(self.hass.config.path(), self.hass.data[DOMAIN_DATA])
            raise web.HTTPFound('/community_settings')

        elif element == 'plugin_url_delete':
            self.hass.data[DOMAIN_DATA]['repos']['plugin'].remove(action)
            await write_to_data_store(self.hass.config.path(), self.hass.data[DOMAIN_DATA])
            raise web.HTTPFound('/community_settings')

        elif element == 'integration_url':
            repo = request.query_string.split('=')[-1]
            if 'http' in repo:
                repo = repo.split('https://github.com/')[-1]
            if repo != "":
                self.hass.data[DOMAIN_DATA]['repos']['integration'].append(repo)
                await self.hass.data[DOMAIN_DATA]['commander'].load_integrations_from_git(repo)
                await write_to_data_store(self.hass.config.path(), self.hass.data[DOMAIN_DATA])
            raise web.HTTPFound('/community_settings')

        elif element == 'plugin_url':
            repo = request.query_string.split('=')[-1]
            if 'http' in repo:
                repo = repo.split('https://github.com/')[-1]
            if repo != "":
                self.hass.data[DOMAIN_DATA]['repos']['plugin'].append(repo)
                await self.hass.data[DOMAIN_DATA]['commander'].load_plugins_from_git(repo)
                await write_to_data_store(self.hass.config.path(), self.hass.data[DOMAIN_DATA])
            raise web.HTTPFound('/community_settings')

        else:
            html = await error_view()
            return web.Response(body=html, content_type="text/html", charset="utf-8")



class CommunityOverview(HomeAssistantView):
    """View to serve the overview."""

    requires_auth = False

    url = r"/community_overview"
    name = "community_overview"

    def __init__(self, hass):
        """Initialize overview."""
        self.hass = hass

    async def get(self, request):
        """View to serve the overview."""
        try:
            html = await self.content()
        except Exception as error:
            _LOGGER.error(error)
            html = await error_view()
        return web.Response(body=html, content_type="text/html", charset="utf-8")


    async def content(self):
        """Content."""
        content = ""

        content += await css()
        content += await ui_header()

        content += "<div class='container''>"
        content += "<h5>CUSTOM INTEGRATIONS</h5>"
        content += await overview(self.hass, 'integration', True)
        content += "<h5>CUSTOM PLUGINS (LOVELACE)</h5>"
        content += await overview(self.hass, 'plugin', True)
        content += "</div>"

        return content

    async def element_view(self, element):
        """element_view."""
        content = ""
        content += await css()
        content += await ui_header()
        content += "<div class='container''>"
        content += await ui_element_view(self.hass.data[DOMAIN_DATA]['elements'][element])
        content += "</div>"
        return content

async def error_view():
    """Return this on error."""
    ex_type, ex_value, ex_traceback = sys.exc_info()
    trace_back = traceback.extract_tb(ex_traceback)
    stack_trace = list()
    for trace in trace_back:
        stack_trace.append(
            "File : %s , Line : %d, Func.Name : %s, Message : %s" % (
                trace[0], trace[1], trace[2], trace[3]))
    pretty_trace = ""
    for trace in stack_trace:
        pretty_trace += """
            {}
        """.format(trace)
    content = await css()
    content += """
        <h2>Something is super wrong...</h2>
        <p>Exception type: {}</p>
        <p>Exception message: {}</p>
        <code class="codeblock">{}</code>
    """.format(ex_type.__name__, ex_value, pretty_trace)

    content += """
    </br></br>
    <a href='https://github.com/custom-components/hacs/issues/new'
        class='waves-effect waves-light btn'
        target="_blank">
        OPEN ISSUE
    </a>
    """
    return content

async def overview(hass, element_type, show_installed_only=False):
    """Overview."""
    content = ""
    elements = []
    if not hass.data[DOMAIN_DATA]['elements']:
        return NO_ELEMENTS
    for entry in hass.data[DOMAIN_DATA]['elements']:
        element = hass.data[DOMAIN_DATA]['elements'][entry]
        if show_installed_only:
            if not element.isinstalled:
                continue
        if element.element_type == element_type:
            elements.append(element)
    if not elements:
        return NO_ELEMENTS
    else:
        for element in elements:
            content += await ui_overview_card(element)
        return content
