from typing import Iterable

from ..abstract import Datastore
from .adapter import Database
from . import Base


class RelationalDatastore(Datastore):
    def __init__(self):
        self.adapter: Database = Database({"dialect": "sqlite"})

    def create_database(self) -> None:
        self.adapter.create()

    def destroy_database(self) -> None:
        self.adapter.destroy()

    def create(self, obj: object) -> None:
        with self.adapter.Session() as sess:
            sess.add(obj)

    def read(self, tablename: str) -> list:
        table = self.adapter.get_table_class(tablename)
        with self.adapter.Session() as sess:
            return sess.query(table).all()

    def retrieve(self, tablename: str, pks: Iterable) -> dict:
        table = self.adapter.get_table_class(tablename)
        with self.adapter.Session() as sess:
            return sess.query(table).get(pks)

    def update(self, tablename: str, pks: Iterable, obj: object):
        pass

    def delete(self, tablename: str, pks: Iterable) -> None:
        pass
