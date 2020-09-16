import typing
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
    def __init__(self, name: str, type: str, identity: OrfIdentifier, version: str, lang: str, source: List):
        self.name = name
        self.type = type
        self.identity = identity
        self.version = version
        self.lang = lang
        self.source = source
