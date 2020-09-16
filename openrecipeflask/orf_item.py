import tarfile

from flask import json

from openrecipeflask.identifier import OrfIdentifier
from openrecipeflask.item import Item, ItemIndex, Metadata


class OrfItem(Item):
    def __init__(self, archive: tarfile.TarFile):
        self._archive = archive

    def __str__(self):
        return f'OrfItem({self._archive.name})'

    @staticmethod
    def from_path(path):
        return OrfItem(tarfile.open(path, 'r:gz'))

    @property
    def index(self) -> ItemIndex:
        return ItemIndex.from_meta(self.meta)

    @property
    def meta(self) -> Metadata:
        j = json.load(self._archive.extractfile('meta.json'))
        return Metadata(j['name'], j['type'], OrfIdentifier.from_dots(j['identity']),
                        j['version'], j['lang'], j['source'])
