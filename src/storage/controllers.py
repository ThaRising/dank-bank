import json
from pathlib import Path
from typing import Union, List, Optional
from inspect import isclass

from drizm_commons.inspect import SQLAIntrospector
from drizm_commons.sqla import Registry, Base, SqlaDeclarativeEncoder
from sqlalchemy.ext.declarative import DeclarativeMeta

from .abstract import CrudInterface


def find_index_by_value_at_key(items: List[dict],
                               key,
                               value) -> Optional[int]:
    """
    Inside of a list of dictionaries,
    find the index of the first dictionary,
    that has a matching value for the given key
    """
    for index, item in enumerate(items):
        if item.get(key) == value:
            return index
    return None


class JsonController(CrudInterface):
    # noinspection PyMethodMayBeStatic
    def _read_file_contents(self, filepath: Path):
        # the default JSON decoder does not accept a file,
        # that has just an empty list in it so we ignore the error
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
            # read the file -> add some content -> overwrite the file
            current_content = self._read_file_contents(filepath)
            current_content.append(self.model_instance)
            json.dump(
                current_content,
                fout,
                indent=4,
                cls=SqlaDeclarativeEncoder
            )

    def update(self, data: dict):
        # update the values on the instance
        for k, v in data.items():
            setattr(self.model_instance, k, v)

        table = SQLAIntrospector(self.model_instance)
        filename = self.db.schema[table.tablename]["file"]

        with open((self.db.path / filename), "w") as fout:
            # read the file -> modify the content -> overwrite the file
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
            # read the file -> delete some content -> overwrite the file
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
             *args, **kwargs) -> Union[list, DeclarativeMeta]:
        table_inspector = SQLAIntrospector(model_class)
        tablename = table_inspector.tablename

        from . import get_storage
        storage = get_storage()

        filename = storage.schema[tablename]["file"]

        if isclass(model_class):
            cls = model_class
        # if the user only passes a model instance,
        # we need to reverse its baseclass to build a new instance from
        else:
            cls = Registry(Base)[table_inspector.classname]
            cls = cls.__class__

        with open((storage.path / filename), "r") as fout:
            current_content = json.load(fout)
            if not current_content:
                return []
            if not kwargs and not args:
                return [cls(**data) for data in current_content]
            if kwargs:
                requested_column, requested_value = list(kwargs.items())[0]
                indexes = [
                    current_content.index(i) for i in current_content
                    if i.get(requested_column) == requested_value
                ]
                return [cls(**current_content[index]) for index in indexes]
            elif args:
                requested_column = SQLAIntrospector(model_class).primary_keys()[0]
                requested_id = args[0]
                index = find_index_by_value_at_key(
                    current_content,
                    requested_column,
                    requested_id
                )
                item = current_content[index]
                return cls(**item)


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
             *args, **kwargs) -> Union[list, DeclarativeMeta]:
        from . import get_storage
        storage = get_storage()

        # if the user has not provided any kwargs like 'pk=3'
        # then we can assume they want all rows of the given table
        if not kwargs and not args:
            with storage.Session() as sess:
                return sess.query(model_class).all()

        # if they did provide kwargs we can filter
        if kwargs:
            with storage.Session() as sess:
                return sess.query(model_class).filter_by(**kwargs).all()

        elif args:
            with storage.Session() as sess:
                return sess.query(model_class).get(args[0])
