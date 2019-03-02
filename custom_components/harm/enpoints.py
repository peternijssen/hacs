"""Crate enpoinst to serve up dynamic files."""
from aiohttp import web
from homeassistant.components.http import HomeAssistantView


class CustomCardsView(HomeAssistantView):
    """View to return a custom_card file."""

    requires_auth = False

    url = r"/customcards/{path:.+}"
    name = "customcards"

    def __init__(self, hadir):
        """Initialize custom_card view."""
        self.hadir = hadir

    async def get(self, request, path):
        """Retrieve custom_card."""
        if '?' in path:
            path = path.split('?')[0]
        file = "{}/www/{}".format(self.hadir, path)
        if os.path.exists(file):
            msg = "Serving /customcards/{path} from /www/{path}".format(
                path=path)
            _LOGGER.debug(msg)
            resp = web.FileResponse(file)
            resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            resp.headers["Pragma"] = "no-cache"
            resp.headers["Expires"] = "0"
            return resp
        else:
            _LOGGER.error("Tried to serve up '%s' but it does not exist", file)
            return None