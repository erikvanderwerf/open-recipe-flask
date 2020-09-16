from openrecipeflask.item import ItemIndex


class DbIndex(ItemIndex):
    def __init__(self, rowid, identifier, version, name):
        super().__init__(identifier, version, name)
        self.rowid = rowid
