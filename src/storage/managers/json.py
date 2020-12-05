import json
from pathlib import Path
from typing import Union, List, Optional
from inspect import isclass

from drizm_commons.inspect import SQLAIntrospector
from drizm_commons.sqla import Registry, Base, SqlaDeclarativeEncoder
from sqlalchemy.ext.declarative import DeclarativeMeta

from .base import BaseManagerInterface


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


class JsonManager(BaseManagerInterface):
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

    # noinspection PyMethodMayBeStatic
    def _save(self, current_content, fout) -> None:
        """ Writes the provided content into the provided file-object """
        json.dump(
            current_content,
            fout,
            indent=4,
            cls=SqlaDeclarativeEncoder
        )

    def save(self):
        table = SQLAIntrospector(self.klass)
        filename = self.db.schema[table.tablename]["file"]
        filepath = self.db.path / filename

        with open(filepath, "w") as fout:
            # read the file -> add some content -> overwrite the file
            current_content = self._read_file_contents(filepath)
            current_content.append(self.klass)
            self._save(current_content, fout)

    def update(self, data: dict):
        # update the values on the instance
        for k, v in data.items():
            setattr(self.klass, k, v)

        table = SQLAIntrospector(self.klass)
        filename = self.db.schema[table.tablename]["file"]

        with open((self.db.path / filename), "w") as fout:
            # read the file -> modify the content -> overwrite the file
            current_content = json.load(fout)
            pk_column = table.primary_keys()[0]
            index = find_index_by_value_at_key(
                current_content,
                pk_column,
                getattr(self.klass, pk_column)
            )
            current_content[index] = self.klass
            json.dump(
                current_content,
                fout,
                indent=4,
                cls=SqlaDeclarativeEncoder
            )

    def delete(self, **kwargs) -> None:
        table = SQLAIntrospector(self.klass)
        filename = self.db.schema[table.tablename]["file"]

        with open((self.db.path / filename), "w") as fout:
            # read the file -> delete some content -> overwrite the file
            current_content = json.load(fout)
            pk_column = table.primary_keys()[0]
            index = find_index_by_value_at_key(
                current_content,
                pk_column,
                getattr(self.klass, pk_column)
            )
            current_content.pop(index)
            json.dump(
                current_content,
                fout,
                indent=4,
                cls=SqlaDeclarativeEncoder
            )

    def read(self, *args, **kwargs) -> Union[list, DeclarativeMeta]:
        table_inspector = SQLAIntrospector(self.klass)
        tablename = table_inspector.tablename

        filename = self.db.schema[tablename]["file"]

        # if the user only passes a model instance,
        # we need to reverse its baseclass to build a new instance from
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
