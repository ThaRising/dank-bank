import json
from typing import List, NoReturn

from drizm_commons.inspect import SQLAIntrospector
from drizm_commons.sqla import Registry, Base, SqlaDeclarativeEncoder

from src.utils import find_index_by_value_at_key
from .base import BaseManagerInterface
from ..exc import ObjectAlreadyExists, ObjectNotFound


class JsonManager(BaseManagerInterface):
    db_type = "json"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.inspect = SQLAIntrospector(self.klass)

        self.filename = self.db.schema[self.inspect.tablename]["file"]
        self.filepath = self.db.path / self.filename

    # noinspection PyMethodMayBeStatic
    def _read_file_contents(self):
        # the default JSON decoder does not accept a file,
        # that has just an empty list in it so we ignore the error
        with open(self.filepath, "r") as fin:
            try:
                content = json.load(fin)
            except ValueError:
                content = []
            return content

    # noinspection PyMethodMayBeStatic
    def _save(self, current_content, fout) -> None:
        """ Writes the provided content into the provided file-object """
        json.dump(current_content, fout, indent=4, cls=SqlaDeclarativeEncoder)

    def _check_unique(self, current_content: List[dict]) -> None:
        pk_column = self._get_identifier_column_name()
        unique_keys = [k for k in self.inspect.unique_keys() if not k == pk_column]

        instance_unique_values = {
            key: getattr(self.klass, key)
            for key in unique_keys
            if key != self._get_identifier_column_name()
        }
        instance_primary_key = {pk_column: self._get_identifier()}

        for entity in current_content:
            entity_unique_values = [entity.get(key) for key in unique_keys]
            entity_primary_key = entity.get(pk_column)

            for (column_name, instance_value), entity_value in zip(
                instance_unique_values.items(), entity_unique_values
            ):
                # The idea here is that if the value already exists,
                # but the primary key is the same then we are just updating the object.
                # If the value does exist on an instance with a different primary key however,
                # that means there is actually a uniqueness violation occurring.
                if instance_value == entity_value and (
                    instance_primary_key != entity_primary_key
                ):
                    raise ObjectAlreadyExists(
                        f"Value '{instance_value}' for Column "
                        f"'{column_name}' of model "
                        f"'{self.klass.__class__.__name__}' is not unique."
                    )

    def save(self):
        current_content = self._read_file_contents()

        with open(self.filepath, "w") as fout:
            # If this finds a result,
            # that means we are possibly updating the object right now
            index = find_index_by_value_at_key(
                current_content,
                self._get_identifier_column_name(),
                self._get_identifier(),
            )

            # read the file -> add some content -> overwrite the file
            try:
                self._check_unique(current_content)

            except Exception as exc:  # noqa too broad exception clause
                # Make sure that in case anything goes wrong,
                # we write the data back into the file.
                # Otherwise even just a UniqueError would result in all data being lost.
                self._save(current_content, fout)
                raise exc

            # We need to check for literal 'None',
            # as an index of 0 would also be Falsy.
            if index is None:
                current_content.append(self.klass)
            else:
                current_content[index] = self.klass

            self._save(current_content, fout)

    def delete(self) -> None:
        current_content = self._read_file_contents()

        with open(self.filepath, "w") as fout:
            # read the file -> delete some content -> overwrite the file
            index = find_index_by_value_at_key(
                current_content,
                self._get_identifier_column_name(),
                self._get_identifier(),
            )
            current_content.pop(index)
            self._save(current_content, fout)

    def _construct_instance(self, data):
        cls = Registry(Base)[self.inspect.classname]
        cls = cls.__class__
        return cls(**data)

    def _not_found(self, identifier) -> NoReturn:
        raise ObjectNotFound(
            f"Object of type '{self.klass.__name__}' "
            f"with primary key '{identifier}', "
            "could not be found."
        )

    def get(self, identifier):
        current_content = self._read_file_contents()
        if not current_content:
            self._not_found(identifier)

        index = find_index_by_value_at_key(
            current_content, self._get_identifier_column_name(), identifier
        )
        if not index:
            self._not_found(identifier)

        item = current_content[index]
        if not item:
            self._not_found(identifier)

        return self._construct_instance(item)

    def filter(self, **kwargs):
        current_content = self._read_file_contents()

        if not current_content:
            return []

        results = []
        for entity in current_content:
            results.append(
                all([entity.get(column) == value for column, value in kwargs.items()])
            )

        entities = []
        for index, matches_filter_params in enumerate(results):
            if matches_filter_params:
                entities.append(self._construct_instance(current_content[index]))

        return entities

    def all(self):
        current_content = self._read_file_contents()

        if not current_content:
            return []

        return [self._construct_instance(entity) for entity in current_content]
