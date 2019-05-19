"""Elements used in the UI."""

async def css():
    """Load CSS."""
    content = """
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">
      <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.8.2/css/all.css" integrity="sha384-oS3vJWv+0UjzBfQzYUhtDYW+Pj2yciDJxpsK1OYPAYjqT085Qq/1cq5FLXAZQ7Ay" crossorigin="anonymous">
      <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>
      <style>
        .yaml {
            font-family: monospace, monospace;
            font-size: 1em;
            border-style: solid;
            border-width: thin;
        }
      </style>
    """

    return content

async def button(target, text):
    """Return a button."""
    content = """
    <a href='{}'
        class='waves-effect waves-light btn'
        onclick="document.getElementById('progressbar').style.display = 'block'">
        {}
    </a>
    """.format(target, text)
    return content

async def ui_header():
    """Generate a header element."""
    content = """
      <div class="navbar-fixed">
        <nav class="nav-extended black">
          <div class="nav-content">
            <ul class="right tabs tabs-transparent">
              <li class="tab"><a href="/community_overview">overview</a></li>
              <li class="tab"><a href="/community_store">store</a></li>
              <li class="tab"><a href="/community_settings">settings</a></li>
            </ul>
          </div>
        </nav>
      </div>
    <div class="progress" id="progressbar" style="display: none">
        <div class="indeterminate"></div>
    </div>
    """
    return content


async def ui_overview_card(element):
    """Generate a UI card element."""
    content = """
      <div class="row">
        <div class="col s12">
          <div class="card blue-grey darken-1">
            <div class="card-content white-text">
              <span class="card-title">{name}</span>
              <p>{description}</p>
            </div>
            <div class="card-action">
              <a href="/community_element/{element}">Manage</a>
            </div>
          </div>
        </div>
      </div>
    """.format(
        name=str(element.name),
        description=str(element.description),
        element=str(element.element_id)
    )

    return content

async def ui_element_view(element):
    """Generate a UI card element."""
    if element.example_image is not None:
        example_image = """</br>
              </br>
              <img src="{}">
              </br>
              """.format(element.example_image)
    else:
        example_image = ""

    if element.example_config is not None:
        example_config = """</br>
              <p>Example configuration:</p>
              <pre class="yaml">{}</pre>
              """.format(element.example_config)
    else:
        example_config = ""

    if element.installed_version is not None:
        installed_version = """</br>
              <p>installed version: {}</p>
              """.format(element.installed_version)
    else:
        installed_version = ""

    if element.isinstalled:
        main_action = "upgrade"
    else:
        main_action = "install"

    content = """
      <div class="row">
        <div class="col s12">
          <div class="card blue-grey darken-1">
            <div class="card-content white-text">
              <span class="card-title">{name}</span>
              <p>{description}</p>
              {installed}
              {example_image}
              {example_config}
            </div>
            <div class="card-action">
              <a href="/community_api/{element}/{main_action}"
                onclick="document.getElementById('progressbar').style.display = 'block'">
                {main_action}
              </a>
            </div>
          </div>
        </div>
      </div>
    """.format(
        main_action=main_action,
        example_image=example_image,
        example_config=example_config,
        name=str(element.name),
        installed=str(installed_version),
        description=str(element.description),
        element=str(element.element_id)
    )

    return content
