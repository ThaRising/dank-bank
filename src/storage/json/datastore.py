from ..abstract import Datastore
from pathlib import Path
from .adapter import JsonAdapter
from typing import Iterable


class JsonDatastore(Datastore):
    def __init__(self, path: Path = None) -> None:
        self.adapter: JsonAdapter = JsonAdapter(path)

    def create(self, obj) -> None:
        self.adapter.write(obj)

    def read(self, tablename: str):
        return self.adapter.read(tablename)

    def retrieve(self, tablename, pks):
        return self.adapter.read_item(tablename, pks)

    def update(self, tablename: str, pks: Iterable, obj: object):
        self.adapter.replace_item(tablename, pks, obj)

    def delete(self, tablename: str, pks: Iterable) -> None:
        self.adapter.replace_item(tablename, pks)

    def create_database(self) -> None:
        self.adapter.initialize_datastore()

    def destroy_database(self) -> None:
        self.adapter.clear_datastore()
