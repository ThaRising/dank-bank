from .base import Base
from configparser import ConfigParser
from sqlalchemy.inspection import inspect
from functools import cached_property
from typing import ClassVar


class Registry:
    __state: ClassVar["Registry"] = None
    schema = ConfigParser()

    @cached_property
    def tables(self):
        return {
            table.name: table for table in Base.metadata.sorted_tables
        }

    def __new__(cls):
        if not cls.__state:
            obj = super().__new__(cls)
            obj._init()
            cls.__state = obj
        return cls.__state

    def _init(self):
        # Check if a mapping has already been loaded
        if not self.schema.sections():
            self.create_mapping()

    def create_mapping(self):
        for table in self.tables.values():
            tablename = table.name
            primary_keys = inspect(table).primary_key
            foreign_keys = [c for c in table.c if c.foreign_keys]
            fk_names = [key.name for key in foreign_keys]
            fk_targets = [
                list(key.foreign_keys)[0].target_fullname for key in foreign_keys
            ]
            self.schema[tablename] = {
                "pks": [key.name for key in primary_keys],
                "fks": {
                    name: target for name, target in zip(fk_names, fk_targets)
                },
                "filename": f"{tablename}.json"
            }

    def reset_mapping(self):
        # Make sure schema is completely destroyed to avoid 2nd gen gc
        del self.schema
        self.schema = ConfigParser()
        # Here we fully need to destroy the instance,
        # in order to reset the cache of cached_property
        del self

    def __getitem__(self, item):
        return self.tables.__getitem__(item)

    def __iter__(self):
        return iter(Base.metadata.sorted_tables)
