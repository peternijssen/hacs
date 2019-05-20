"""Log handler."""
import logging

_LOGGER = logging.getLogger(__name__)


async def get_log_file_content(hass):
    """Get logfile content."""
    _LOGGER.debug("Generating log contents")

    log_file = "{}/home-assistant.log".format(hass.config.path())
    interesting = ""

    try:
        with open(log_file, encoding='utf-8', errors='ignore') as localfile:
            for line in localfile.readlines():
                if "[custom_components.hacs" in line:
                    line = line.replace("(MainThread) [custom_components.hacs", "- hacs").replace("]", " -")
                    interesting += "<pre style='margin: 0'>{}</pre>".format(line)
            localfile.close()
    except Exception as error:  # pylint: disable=W0703
        msg = "Could not load logfile from {} - {}".format(log_file, error)
        _LOGGER.debug(msg)
    return interesting
