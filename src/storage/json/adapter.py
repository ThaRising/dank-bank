from ..sql import Base
from .encoder import AlchemyEncoder
from .decoder import OrmDecoder
from sqlalchemy.inspection import inspect
from pathlib import Path
from typing import ClassVar, Union
from configparser import ConfigParser
import json
import ast
import shutil
from src.schema import Registry


class JsonAdapter:
    encoder: ClassVar = AlchemyEncoder
    decoder: ClassVar = OrmDecoder
    table_mapping_name = ".tables"
    schema = ConfigParser()

    def __init__(self,
                 path: Union[Path, str] = "None") -> None:
        self.db_path = path

    def initialize_datastore(self) -> None:
        """ Creates or loads the database """
        if self._table_db_exists():  # load the table mapping
            self._load_table_mapping()
        else:  # create the table mapping and write it
            self.db_path.mkdir(exist_ok=True)
            self._create_table_mapping()
            self._create_table_structure()

    def clear_datastore(self) -> None:
        """ Deletes the local datastore """
        shutil.rmtree(self.db_path)
        self.schema = ConfigParser()

    def _table_db_exists(self):
        """ Check if the database and an existing mapping already exists """
        if not self.db_path.exists():
            return False

        # If the folder exists but there is no mapping file
        if not (self.db_path / self.table_mapping_name).exists():
            return False

        return True

    def _create_table_mapping(self):
        for table in Registry():
            tablename = table.name
            self.schema[tablename] = {
                "pks": [key.name for key in inspect(table).primary_key],
                "fks": inspect(table).foreign_keys,
                "filename": f"{tablename}.json"
            }
        with open(self.db_path / self.table_mapping_name, "w") as fout:
            self.schema.write(fout)

    def _create_table_structure(self):
        for section in self.schema.sections():
            filename = self.db_path / self.schema[section]["filename"]
            with open(filename, "w") as fout:
                fout.write("[]")

    def _load_table_mapping(self):
        self.schema.read(self.db_path / self.table_mapping_name)

    def _get_table_store(self, tablename: str) -> Path:
        try:
            table = self.schema[tablename]["filename"]
        except KeyError:
            raise ValueError(f"Table {tablename} does not exist")
        return self.db_path / table

    def read(self, tablename):
        with open(self._get_table_store(tablename), "r") as fin:
            return json.load(fin, cls=self.decoder)

    def read_item(self, tablename, pks):
        self._get_table_store(tablename)
        identifiers = ast.literal_eval(self.schema[tablename]["pks"])
        identifiers = {k: v for k, v in zip(identifiers, pks)}
        if len(identifiers) != len(pks):
            raise ValueError
        items = self.read(tablename)
        for item in items:
            matches = [
                (
                    True if item.get(pk_name) == pk_value else False
                ) for pk_name, pk_value in identifiers.items()
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
