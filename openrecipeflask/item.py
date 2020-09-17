from abc import abstractmethod, ABC
from typing import List

from openrecipeflask.identifier import OrfIdentifier


class Item(ABC):
    @property
    @abstractmethod
    def index(self) -> 'ItemIndex':
        raise NotImplementedError()

    @property
    @abstractmethod
    def meta(self) -> 'Metadata':
        raise NotImplementedError()


class ItemIndex(ABC):
    def __init__(self, identifier: OrfIdentifier, version: str, name: str):
        self.identifier = identifier
        self.version = version
        self.name = name

    @classmethod
    def from_meta(cls, meta: 'Metadata'):
        return ItemIndex(meta.identity, meta.version, meta.name)


class Metadata(ABC):
    def __init__(self, identity: OrfIdentifier, version: str, name: str, type: str, lang: str, source: List):
        self.identity = identity
        self.version = version
        self.name = name
        self.type = type
        self.lang = lang
        self.source = source


def json_index_serializer(item: ItemIndex):
    return {'id': item.identifier.dot, 'ver': item.version, 'name': item.name}


def json_meta_serializer(meta: Metadata):
    return {'id': meta.identity.dot, 'ver': meta.version, 'name': meta.name,
            'type': meta.type, 'lang': meta.lang, 'source': meta.source}
