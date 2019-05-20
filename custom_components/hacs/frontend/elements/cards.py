"""Card elements."""


async def overview_card(element):
    """Generate a UI card element."""
    return """
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
