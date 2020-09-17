from abc import ABC
from pathlib import Path
from sqlite3.dbapi2 import Cursor
from typing import List, Tuple, Iterator

from openrecipeflask.identifier import OrfIdentifier
from openrecipeflask.item import ItemIndex
from openrecipeflask.orf_item import OrfItem
from openrecipeflask.repo.changeable import Changeable
from openrecipeflask.repo.exceptions import NotFound
from openrecipeflask.repo.index import DbIndex


class Dao(ABC):
    def __init__(self, parent: Changeable):
        self._parent = parent


class IndexDao(Dao):
    def __init__(self, parent: Changeable, cursor: Cursor):
        super().__init__(parent)
        self._cur = cursor

    def __str__(self):
        return 'Index DAO'

    def __contains__(self, index: ItemIndex):
        if not isinstance(index, ItemIndex):
            raise TypeError(f'{index} must be an ItemIndex')
        self._cur.execute('SELECT EXISTS(SELECT * FROM orf_index WHERE identifier=?)', (index.identifier.dot,))
        one = bool(self._cur.fetchone()[0])
        return one

    @staticmethod
    def _decode_index(cols: List) -> DbIndex:
        cols[1] = OrfIdentifier(cols[1].split('.'))
        return DbIndex(*cols)

    @staticmethod
    def _encode_index(index: ItemIndex) -> Tuple:
        return index.identifier.dot, index.version, index.name

    def insert(self, index: ItemIndex, link_to_file: Path = None):
        if not isinstance(index, ItemIndex):
            raise TypeError('index must be an ItemIndex')
        orf_index = IndexDao._encode_index(index)
        self._cur.execute('INSERT INTO orf_index (identifier, version, name) VALUES (?, ?, ?)', orf_index)
        self._parent.changed()
        if link_to_file:
            self._cur.execute('INSERT INTO translation (idx_row, filepath) VALUES (?, ?)',
                              (self._cur.lastrowid, link_to_file.as_posix()))

    def list(self) -> Iterator[ItemIndex]:
        self._cur.execute('SELECT * FROM orf_index')
        return (IndexDao._decode_index(list(x)) for x in self._cur.fetchall())

    def by_identifier(self, identifier: str):
        raise NotImplementedError()


class ItemDao(Dao):
    def __init__(self, parent: Changeable, cursor: Cursor):
        super().__init__(parent)
        self._cur = cursor

    def by_identifier(self, identifier: OrfIdentifier):
        self._cur.execute('SELECT filepath FROM translation WHERE idx_row = '
                          '(SELECT rowid FROM orf_index WHERE identifier = ?)', (identifier.dot,))
        try:
            filepath = self._cur.fetchone()[0]
        except TypeError:
            raise NotFound(identifier)
        return OrfItem.from_path(filepath)
