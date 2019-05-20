"""CommunityAPI View for HACS."""
import logging
from aiohttp import web
from homeassistant.components.http import HomeAssistantView

from custom_components.hacs.const import DOMAIN_DATA
from custom_components.hacs.frontend.views import error_view
from custom_components.hacs.frontend.elements import style, header, generic_button

_LOGGER = logging.getLogger(__name__)


class CommunitySettings(HomeAssistantView):
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
        content += await style()
        content += await header()

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
                <input type="submit" value="ADD" style="margin-left: 2%" onclick="document.getElementById('progressbar').style.display = 'block'">
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
                <input type="submit" value="ADD" style="margin-left: 2%" onclick="document.getElementById('progressbar').style.display = 'block'">
            </form> 
        </div>
        """

        # Reload button
        content += "</br>"
        content += "</br>"
        content += "</br>"
        content += await generic_button('/community_api/self/reload', 'RELOAD DATA')
        content += """
            <a href='https://github.com/custom-components/hacs/issues/new'
                class='waves-effect waves-light btn'
                target="_blank" style="float: right">
                OPEN ISSUE
            </a>
        """
        content += "</div>"
        return content