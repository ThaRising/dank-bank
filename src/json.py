import json
import os
import shutil
from configparser import ConfigParser
from pathlib import Path
from typing import Any, Union

from drizm_commons.sqla import Base
from re import sub
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta


def is_dunder(name: str) -> bool:
    if name[:2] and name[-2:] in ("__",):
        return True
    return False


class AlchemyEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        # Check if the class is an SQLAlchemy table
        if isinstance(o.__class__, DeclarativeMeta):
            fields = {}
            # Get all columns of the table
            for field in [f for f in dir(o) if not is_dunder(f) and f != "metadata"]:
                # Obtain the value of the field
                data = getattr(o, field)
                try:  # Try JSON encoding the field, if it fails, skip the field
                    json.dumps(data)
                    fields[field] = data
                except TypeError:
                    pass  # TODO: implement edge cases here
            return fields

        # If it is not an SQLAlchemy table use the default encoder
        return super(AlchemyEncoder, self).default(o)


class Inspector:
    def __init__(self, o__):
        self.schema = o__

    def primary_keys(self) -> list:
        return [c.key for c in inspect(self.schema).primary_key.columns]

    def unique_keys(self) -> list:
        return [
            c.name for c in self.schema.c if any(
                [c.primary_key, c.unique]
            )
        ]

    def foreign_keys(self, columns_only: bool = False) -> Union[list, dict]:
        foreign_keys = [c for c in self.schema.c if c.foreign_keys]
        fk_names = [key.name for key in foreign_keys]
        if columns_only:
            return fk_names
        fk_targets = [
            list(key.foreign_keys)[0].target_fullname for key in foreign_keys
        ]
        return {
            name: target for name, target in zip(fk_names, fk_targets)
        }


class JsonAdapter:
    def __init__(self) -> None:
        self.schema = ConfigParser()
        root = os.environ.get("PYTHONPATH").split(os.pathsep)[0]
        self.path = Path(root) / ".json_db"
        if self.path.exists():
            self.destroy()
        self.path.mkdir()
        self._tbl_cls_from_meta("konto")

    def create(self) -> None:
        for table in Base.metadata.sorted_tables:
            t = Inspector(table)
            filename = f"{table.name}.json"
            with open((self.path / filename), "w") as fout:
                json.dump([], fout)
            data = {
                "file": filename,
                "pk": t.primary_keys(),
                "uq": t.unique_keys(),
                "fk": t.foreign_keys()
            }
            self.schema[table.name] = data
        table_map = Path(self.path) / "tbl_map.ini"
        table_map.touch()
        with open(table_map, "w") as fout:
            self.schema.write(fout)

    def destroy(self):
        shutil.rmtree(str(self.path))

    def _tbl_cls_from_tablename(self, tablename: str):
        tbl_name = lambda name: sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        refs = {tbl_name(c): c for c in Base._decl_class_registry.keys()}
        classname = refs.get(tablename)
        return Base._decl_class_registry.get(classname)

    def _tbl_cls_from_classname(self, classname: str):
        return Base._decl_class_registry.get(classname)
