import os
from unittest import TestCase

from openrecipeflask.orf_item import OrfItem

SERVE_DIR = 'res'
TEST_ITEM = 'W6T84GW54615'


class TestTarItem(TestCase):
    item: OrfItem

    @classmethod
    def setUpClass(cls) -> None:
        path = os.path.join(SERVE_DIR, f'root.{TEST_ITEM}.1.orf')
        cls.item = OrfItem.from_path(path)

    def test_meta(self):
        print(self.item.meta)
