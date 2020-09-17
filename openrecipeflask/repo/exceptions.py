from openrecipeflask.identifier import OrfIdentifier


class NotFound(Exception):
    """Raised when something could not be found in database."""
    def __init__(self, identifier: OrfIdentifier):
        super(NotFound, self).__init__(identifier.dot)
