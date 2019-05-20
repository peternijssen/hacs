"""Return a generic button."""

async def generic_button(target, text):
    """Return a button, and activate the progressbar."""
    return """
    <a href='{}'
        class='waves-effect waves-light btn'
        onclick="document.getElementById('progressbar').style.display = 'block'">
        {}
    </a>
    """.format(target, text)
