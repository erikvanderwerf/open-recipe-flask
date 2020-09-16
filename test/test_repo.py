import os
import tempfile
from pprint import pprint
from tempfile import TemporaryDirectory
from unittest import TestCase

from openrecipeflask.repo import Repository


class TestRepo(TestCase):
    tmp_dir: TemporaryDirectory

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()

    def test_open(self):
        # TODO Replace with fixture
        with self.tmp_dir as dir:
            db_file = os.path.join(dir, 'db.sqlite')
            r = Repository(db_file)
            print(db_file)
            with r as conn:
                pprint(list(conn.iterdump()))
