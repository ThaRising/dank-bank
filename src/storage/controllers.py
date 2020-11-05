import json
from pathlib import Path
from typing import Union, List, Optional

from drizm_commons.inspect import SQLAIntrospector
from drizm_commons.sqla import Registry, Base, SqlaDeclarativeEncoder
from sqlalchemy.ext.declarative import DeclarativeMeta

from .abstract import CrudInterface


def find_index_by_value_at_key(items: List[dict],
                               key,
                               value) -> Optional[int]:
    for index, item in enumerate(items):
        if item.get(key) == value:
            return index
    return None


class JsonController(CrudInterface):
    # noinspection PyMethodMayBeStatic
    def _read_file_contents(self, filepath: Path):
        with open(filepath, "r") as fin:
            try:
                content = json.load(fin)
            except ValueError:
                content = []
            return content

    def create(self):
        table = SQLAIntrospector(self.model_instance)
        filename = self.db.schema[table.tablename]["file"]
        filepath = self.db.path / filename

        with open(filepath, "w") as fout:
            # read the file -> modify the content -> overwrite the file
            current_content = self._read_file_contents(filepath)
            current_content.append(self.model_instance)
            json.dump(
                current_content,
                fout,
                indent=4,
                cls=SqlaDeclarativeEncoder
            )

    def update(self, data: dict):
        # update the values based on passed data
        for k, v in data.items():
            setattr(self.model_instance, k, v)
        table = SQLAIntrospector(self.model_instance)
        filename = self.db.schema[table.tablename]["file"]

        with open((self.db.path / filename), "w") as fout:
            current_content = json.load(fout)
            pk_column = table.primary_keys()[0]
            index = find_index_by_value_at_key(
                current_content,
                pk_column,
                getattr(self.model_instance, pk_column)
            )
            current_content[index] = self.model_instance
            json.dump(
                current_content,
                fout,
                indent=4,
                cls=SqlaDeclarativeEncoder
            )

    def delete(self, **kwargs) -> None:
        table = SQLAIntrospector(self.model_instance)
        filename = self.db.schema[table.tablename]["file"]

        with open((self.db.path / filename), "w") as fout:
            current_content = json.load(fout)
            pk_column = table.primary_keys()[0]
            index = find_index_by_value_at_key(
                current_content,
                pk_column,
                getattr(self.model_instance, pk_column)
            )
            current_content.pop(index)
            json.dump(
                current_content,
                fout,
                indent=4,
                cls=SqlaDeclarativeEncoder
            )

    @staticmethod
    def read(model_class: DeclarativeMeta,
             storage_instance,
             **kwargs) -> Union[list, DeclarativeMeta]:
        tablename = model_class.__tablename__
        filename = storage_instance.schema[tablename]["file"]
        cls = Registry(Base).table_class_from_tablename(tablename)
        with open((storage_instance.path / filename), "r") as fout:
            current_content = json.load(fout)
            if kwargs:
                requested_column, requested_id = list(kwargs.items())[0]
                index = find_index_by_value_at_key(
                    current_content,
                    requested_column,
                    requested_id
                )
                item = current_content[index]
                return cls.__class__(**item)
            else:
                return [cls(**data) for data in current_content]


class SqlController(CrudInterface):
    def create(self) -> None:
        with self.db.Session() as sess:
            sess.add(self.model_instance)

    def update(self, data: dict) -> None:
        with self.db.Session():
            for k, v in data.items():
                setattr(self.model_instance, k, v)

    def delete(self, **kwargs) -> None:
        with self.db.Session() as sess:
            sess.delete(self.model_instance)

    @staticmethod
    def read(model_class: DeclarativeMeta,
             storage_instance,
             **kwargs) -> Union[list, DeclarativeMeta]:
        if not kwargs:
            with storage_instance.Session() as sess:
                return sess.query(model_class).all()
        with storage_instance.Session() as sess:
            return sess.query(model_class).filter_by(**kwargs).all()
