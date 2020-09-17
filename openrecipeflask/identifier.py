class OrfIdentifier:
    def __init__(self, parts):
        if not isinstance(parts, (list, tuple)):
            raise TypeError('parts must be a list or tuple')
        self._parts = parts

    @staticmethod
    def from_url(path: str):
        return OrfIdentifier(path.split('/'))

    @staticmethod
    def from_dots(dots: str):
        return OrfIdentifier(dots.split('.'))

    @property
    def dot(self):
        return '.'.join(self._parts)
