"""Generate UI elements for a element."""
import logging

_LOGGER = logging.getLogger(__name__)


class Generate:
    """Generator for UI elements."""

    def __init__(self, hass, element):
        """Initialize."""
        self.hass = hass
        self.element = element

    async def authors(self):
        """Generate authors."""
        _LOGGER.debug("Generating authors for %s", self.element.element_id)

        if not self.element.authors:
            return ""

        authors = "<p>Author(s): "
        for author in self.element.authors:

            if "@" in author:
                author = author.split("@")[-1]

            authors += """
              <a href="https://github.com/{author}"
                target="_blank"
                style="margin: 2">
                @{author}
              </a>
            """.format(author=author)

        authors += "</p>"
        return authors

    async def avaiable_version(self):
        """Generate avaiable version."""
        _LOGGER.debug("Generating avaiable version for %s", self.element.element_id)

        return """
          <p>
            Available version: {}
          </p>
        """.format(self.element.avaiable_version)

    async def description(self):
        """Generate description version."""
        _LOGGER.debug("Generating description for %s", self.element.element_id)

        return """
          <p>
            {}
          </p>
          </br>
        """.format(self.element.description)

    async def element_note(self):
        """Generate element note."""
        _LOGGER.debug("Generating element note for %s", self.element.element_id)

        if self.element.element_type == "integration":
            return """
              </br>
              <i>
                When installed, this will be located in '{}/custom_components/{}/',
                you still need to add it to your 'configuration.yaml' file.
              </i>
              </br></br>
              <i>
                To learn more about how to configure this,
                click the "REPO" button to get to the repoistory for this integration.
              </i>
            """.format(self.hass.config.path(), self.element.element_id)

        elif self.element.element_type == "plugin":
            if 'lovelace-' in self.element.element_id:
                file_name = self.element.element_id.split('lovelace-')[-1]
            else:
                file_name = self.element.element_id

            return """
              </br>
              <i>
                When installed, this will be located in '{config}/www/community/{element}',
                you still need to add it to your lovelace configuration ('ui-lovelace.yaml' or the raw UI config editor).
              </i>
              </br>
              <i>
                When you add this to your configuration use this as the URL:
              </i>
              </br>
              <i>
                '/community_plugin/{element}/{file_name}.js'
              </i>
              </br></br>
              <i>
                To learn more about how to configure this,
                click the "REPO" button to get to the repoistory for this plugin.
              </i>
            """.format(config=self.hass.config.path(), element=self.element.element_id, file_name=file_name)
        else:
            return ""

    async def example_config(self):
        """Generate example config."""
        _LOGGER.debug("Generating example config for %s", self.element.element_id)

        if self.element.example_config is None:
            return ""

        return """
          </br>
          <p>
            Example configuration:
          </p>
          <pre class="yaml"
            {}
          </pre>
          </br>
        """.format(self.element.example_config)

    async def example_image(self):
        """Generate example image."""
        _LOGGER.debug("Generating example image for %s", self.element.element_id)

        if self.element.example_image is None:
            return ""

        return """
          </br></br>
          <img src="{}" style="max-width: 100%">
          </br>
        """.format(self.element.example_image)

    async def installed_version(self):
        """Generate installed version."""
        _LOGGER.debug("Generating installed version for %s", self.element.element_id)

        if self.element.installed_version is None:
            return ""

        return """
          </br>
          <p>
            Installed version: {}
          </p>
        """.format(self.element.installed_version)

    async def main_action(self):
        """Generate main action."""
        _LOGGER.debug("Generating main action for %s", self.element.element_id)

        if not self.element.isinstalled:
            action = "install"
            title = action

        else:
            if self.element.installed_version == self.element.avaiable_version:
                action = "install"
                title = "reinstall"
            else:
                action = "upgrade"
                title = action

        return """
          <a href="/community_api/{}/{}"
            onclick="document.getElementById('progressbar').style.display = 'block'">
            {}
          </a>
        """.format(self.element.element_id, action, title)

    async def restart_pending(self):
        """Generate main action."""
        _LOGGER.debug("Generating main action for %s", self.element.element_id)

        if not self.element.restart_pending:
            return ""

        return """

        """.format()

    async def uninstall(self):
        """Generate main action."""
        _LOGGER.debug("Generating main action for %s", self.element.element_id)

        if not self.element.isinstalled:
            return ""

        return """
          <a href="/community_api/{}/uninstall"
            style="float: right; color: #a70000; font-weight: bold;"
            onclick="document.getElementById('progressbar').style.display = 'block'">
            UNINSTALL
          </a>
        """.format(self.element.element_id)
