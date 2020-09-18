from ..sql import Base
from .encoder import AlchemyEncoder
from sqlalchemy.inspection import inspect
from pathlib import Path
from typing import ClassVar, Union
from configparser import ConfigParser
import json
import ast
import shutil


class JsonAdapter:
    encoder: ClassVar = AlchemyEncoder
    db_path: ClassVar = ""

    _table_mapping_name = ".tables"
    _schema = ConfigParser()

    def __init__(self, path: Union[Path, str] = None) -> None:
        self.db_path = self.db_path or path

    def initialize_datastore(self):
        if self._table_db_exists():  # load the table mapping
            self._load_table_mapping()
        else:  # create the table mapping and write it
            self.db_path.mkdir()
            self._create_table_mapping()
            self._create_table_structure()

    def clear_datastore(self):
        shutil.rmtree(self.db_path)
        self._schema = ConfigParser()

    def _table_db_exists(self):
        if not self.db_path.exists():
            return False
        return True

    def _create_table_mapping(self):
        for table in Base.metadata.sorted_tables:
            tablename = table.name
            self._schema[tablename] = {
                "pks": [key.name for key in inspect(table).primary_key],
                "filename": f"{tablename}.json"
            }
        with open(self.db_path / self._table_mapping_name, "w") as fout:
            self._schema.write(fout)

    def _create_table_structure(self):
        for section in self._schema.sections():
            filename = self.db_path / self._schema[section]["filename"]
            with open(filename, "w") as fout:
                fout.write("[]")

    def _load_table_mapping(self):
        self._schema.read(self.db_path / self._table_mapping_name)

    def _get_table_store(self, tablename: str) -> Path:
        try:
            table = self._schema[tablename]["filename"]
        except KeyError:
            raise ValueError(f"Table {tablename} does not exist")
        return self.db_path / table

    def read(self, tablename):
        with open(self._get_table_store(tablename), "r") as fin:
            return json.load(fin)

    def read_item(self, tablename, pks):
        self._get_table_store(tablename)
        identifiers = ast.literal_eval(self._schema[tablename]["pks"])
        identifiers = {k: v for k, v in zip(identifiers, pks)}
        if len(identifiers) != len(pks):
            raise ValueError
        items = self.read(tablename)
        for item in items:
            matches = [
                (True if item.get(pk_name) == pk_value else False) for pk_name, pk_value in identifiers.items()
            ]
            if all(matches):
                return item

    def write(self, obj):
        tablename = obj.__tablename__
        existing = self.read(tablename)
        existing.append(obj)
        with open(self._get_table_store(tablename), "w") as fout:
            json.dump(existing, fout, indent=4, cls=AlchemyEncoder)

    def replace_item(self, tablename, pks, obj=None):
        item = self.read_item(tablename, pks)
        items: list = self.read(tablename)
        index_ = items.index(item)
        if not obj:
            items.pop(index_)  # delete operation
        else:
            items[index_] = obj
        with open(self._get_table_store(tablename), "w") as fout:
            json.dump(items, fout, indent=4, cls=AlchemyEncoder)
