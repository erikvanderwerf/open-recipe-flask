import hashlib
import logging
import os
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime, tzinfo, timezone
from pathlib import Path
from sqlite3 import Connection, Cursor
from threading import Lock


__all__ = ['Repository']

from typing import Iterator, Tuple, List, Optional

from openrecipeflask.identifier import OrfIdentifier
from openrecipeflask.item import Item, ItemIndex
from openrecipeflask.repo.index import DbIndex

logger = logging.getLogger('orf.repo')


SQLITE_SCHEMA = """
CREATE TABLE private_meta (
    date         TEXT PRIMARY KEY,
    schema_hash  BLOB NOT NULL,
    cwd          TEXT NOT NULL
);

CREATE TABLE orf_index (
    rowid      INTEGER PRIMARY KEY,
    identifier TEXT NOT NULL,
    version    TEXT NOT NULL,
    name       TEXT NOT NULL
);

CREATE TABLE translation (
    identifier INTEGER PRIMARY KEY,
    filepath   TEXT NOT NULL,
    
    FOREIGN KEY (identifier)
        REFERENCES orf_index (identifier)
) WITHOUT ROWID;
"""
SCHEMA_HASH = hashlib.md5(SQLITE_SCHEMA.encode()).digest()


class Repository:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._conn: Optional[Connection] = None
        self._active: Optional[_ActiveRepository] = None
        self._lock = Lock()

    def __enter__(self) -> '_ActiveRepository':
        with self._lock:
            if self._conn is not None:
                raise ValueError('A connection to the database with this '
                                 'object has already been made.')
            while self._conn is None:
                logger.debug('opening Repository')
                first_run = not self.db_path.exists()
                self._conn = sqlite3.connect(self.db_path)
                if not first_run and not self._verify(self._conn):
                    logger.info('repository verify failed. recreating.')
                    self._conn.close()
                    self._conn = None
                    os.remove(self.db_path)
                    continue
                if first_run:
                    Repository._first_run(self._conn)
            self._active = _ActiveRepository(self._conn)
        return self._active

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()
        valid = self._active.valid
        with self._lock:
            self._conn = None
            self._active = None
        if exc_type is None and not valid:
            raise sqlite3.ProgrammingError('Programmer did not commit or rollback')
        return False

    @staticmethod
    def _first_run(conn: Connection):
        """Initialize SQLite database from nothing."""
        utc_now = datetime.now(timezone.utc).isoformat()
        cur = conn.cursor()
        cur.executescript(SQLITE_SCHEMA)
        cur.execute("INSERT INTO private_meta (date, schema_hash, cwd) VALUES (?, ?, ?)",
                    (utc_now, SCHEMA_HASH, os.getcwd()))
        cur.close()
        conn.commit()

    @staticmethod
    def _verify(conn: Connection):
        """Ensure that existing SQLite DB """
        cur = conn.cursor()
        cur.execute("SELECT schema_hash, cwd FROM private_meta LIMIT 1")
        schema_hash, old_cwd = cur.fetchone()
        if SCHEMA_HASH != schema_hash:
            return False
        if os.getcwd() != old_cwd:
            return False
        return True


class Changeable(ABC):
    @abstractmethod
    def changed(self):
        raise NotImplementedError()


class _ActiveRepository(Changeable):
    def __init__(self, connection: Connection):
        self._conn = connection
        self._is_commit = False
        self._is_rollback = False
        self._dirty = False

    def __str__(self):
        return f'Active Connection for {self._conn}'

    def changed(self):
        self._dirty = True

    def commit(self):
        self._conn.commit()
        self._is_commit = True

    @property
    def index(self):
        return _Index(self, self._conn.cursor())

    def iterdump(self):
        return self._conn.iterdump()

    def rollback(self):
        self._conn.rollback()
        self._is_rollback = True

    @property
    def valid(self):
        return (not self._dirty) or self._is_commit or self._is_rollback


class _Index:
    def __init__(self, parent: Changeable, cursor: Cursor):
        self._parent = parent
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
        cols[1] = OrfIdentifier(cols[1])
        return DbIndex(*cols)

    @staticmethod
    def _encode_index(index: ItemIndex) -> Tuple:
        return index.identifier.dot, index.version, index.name

    def insert(self, index: ItemIndex, link_to_file: Path = None):
        if not isinstance(index, ItemIndex):
            raise TypeError('index must be an ItemIndex')
        orf_index = _Index._encode_index(index)
        self._cur.execute('INSERT INTO orf_index (identifier, version, name) VALUES (?, ?, ?)', orf_index)
        self._parent.changed()
        if link_to_file:
            self._cur.execute('INSERT INTO translation (identifier, filepath) VALUES (?, ?)',
                              (self._cur.lastrowid, link_to_file.as_posix()))

    def list(self) -> Iterator[ItemIndex]:
        self._cur.execute('SELECT * FROM orf_index')
        return (_Index._decode_index(x) for x in self._cur.fetchall())

    def by_identifier(self, identifier: str):
        raise NotImplementedError()
