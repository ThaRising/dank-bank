import datetime
import json

from drizm_commons.inspect import SQLAIntrospector
from drizm_commons.sqla import Registry, Base, SqlaDeclarativeEncoder

from .base import BaseManagerInterface
from ..exc import ObjectAlreadyExists, ObjectNotFound
from src.utils import find_index_by_value_at_key


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
        # TODO all of this is just a band-aid fix
        for index, elem in enumerate(current_content):
            if type(elem) != dict:
                obj = {
                    attr: getattr(
                        elem, attr
                    ) for attr in elem.__dict__ if not attr.startswith("_")
                }
                for k, v in obj.items():
                    if type(v) == datetime.date or type(v) == datetime.datetime:
                        obj[k] = v.isoformat()
                current_content[index] = obj
        json.dump(
            current_content,
            fout,
            indent=4,
            cls=SqlaDeclarativeEncoder
        )

    def _check_unique(self, current_content: dict) -> None:
        unique_keys = self.inspect.unique_keys()

        # Get the values of the unique columns on our instance
        unique_values = {
            key: getattr(self.klass, key) for key in unique_keys
        }

        for entity in current_content:
            entity: dict
            entity_unique_values = [
                entity.get(key) for key in unique_keys
            ]
            for (attr_name, instance_value), entity_value in zip(
                unique_values.items(), entity_unique_values
            ):
                if instance_value == entity_value:
                    raise ObjectAlreadyExists(
                        f"Value '{instance_value}' for Column "
                        f"'{attr_name}' of model "
                        f"'{self.klass.__class__.__name__}' is not unique."
                    )

    def save(self):
        current_content = self._read_file_contents()

        with open(self.filepath, "w") as fout:
            # read the file -> add some content -> overwrite the file
            try:
                self._check_unique(current_content)
            finally:
                self._save(current_content, fout)

            current_content.append(self.klass)
            self._save(current_content, fout)

    def update(self, data: dict):
        # update the values on the instance
        for k, v in data.items():
            setattr(self.klass, k, v)

        with open(self.filepath, "w") as fout:
            # read the file -> modify the content -> overwrite the file
            current_content = json.load(fout)
            index = find_index_by_value_at_key(
                current_content,
                self._get_identifier_column_name(),
                self._get_identifier()
            )
            current_content[index] = self.klass
            self._save(current_content, fout)

    def delete(self) -> None:
        with open(self.filepath, "w") as fout:
            # read the file -> delete some content -> overwrite the file
            current_content = json.load(fout)
            index = find_index_by_value_at_key(
                current_content,
                self._get_identifier_column_name(),
                self._get_identifier()
            )
            current_content.pop(index)
            self._save(current_content, fout)

    def _construct_instance(self, data):
        cls = Registry(Base)[self.inspect.classname]
        cls = cls.__class__
        return cls(**data)

    def _read(self, *args, **kwargs):
        with open(self.filepath, "r") as fout:
            current_content = self._read_file_contents()

            if not args and not kwargs:
                # This is the case for .all()
                if not current_content:
                    return []

                return [
                    self._construct_instance(
                        entity
                    ) for entity in current_content
                ]

            if args:
                # This is the case for .get()
                pk = args[0]

                if not current_content:
                    raise ObjectNotFound(
                        f"Object of type '{self.klass.__name__}' "
                        f"with primary key '{pk}', "
                        "could not be found."
                    )

                index = find_index_by_value_at_key(
                    current_content,
                    self._get_identifier_column_name(),
                    pk
                )
                if not index:
                    raise ObjectNotFound(
                        f"Object of type '{self.klass.__name__}' "
                        f"with primary key '{pk}', "
                        f"could not be found."
                    )

                item = current_content[index]
                if not item:
                    raise ObjectNotFound(
                        f"Object of type '{self.klass.__name__}' "
                        f"with primary key '{pk}', "
                        f"could not be found."
                    )

                return self._construct_instance(item)

            if kwargs:
                # This is the case for .filter()
                if not current_content:
                    return []

                results = []
                for entity in current_content:
                    results.append(
                        all([
                            entity.get(
                                column
                            ) == value for column, value in kwargs.items()
                        ])
                    )

                entities = []
                for index, matches_filter_params in enumerate(results):
                    if matches_filter_params:
                        entities.append(
                            self._construct_instance(current_content[index])
                        )

                return entities
