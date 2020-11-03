from functools import lru_cache
from typing import Union, Type

from drizm_commons.sqla import Database
from sqlalchemy.ext.declarative import DeclarativeMeta

from .json import JsonAdapter, AlchemyEncoder, Inspector
from .abstract import CrudInterface
import json


class JsonController(CrudInterface):
    def create(self):
        tablename = self.model_instance.__tablename__
        filename = self.db.schema[tablename].file
        with open((self.db.path / filename), "w") as fout:
            existing = json.load(fout)
            existing.append(self.model_instance)
            json.dump(existing, fout, indent=4, cls=AlchemyEncoder)

    def update(self, data: dict):
        for k, v in data.items():
            setattr(self.model_instance, k, v)
        tablename = self.model_instance.__tablename__
        filename = self.db.schema[tablename].file
        with open((self.db.path / filename), "w") as fout:
            existing = json.load(fout)
            pk_column = Inspector(self.model_instance).primary_keys()[0]
            pks = [d.get(pk_column) for d in existing]
            nr = pks.index(getattr(self.model_instance, pk_column))
            existing[nr] = self.model_instance
            json.dump(existing, fout, indent=4, cls=AlchemyEncoder)

    def delete(self, **kwargs) -> None:
        tablename = self.model_instance.__tablename__
        filename = self.db.schema[tablename].file
        with open((self.db.path / filename), "w") as fout:
            existing = json.load(fout)
            pk_column = Inspector(self.model_instance).primary_keys()[0]
            pks = [d.get(pk_column) for d in existing]
            nr = pks.index(getattr(self.model_instance, pk_column))
            existing.pop(nr)
            json.dump(existing, fout, indent=4, cls=AlchemyEncoder)

    @staticmethod
    def read(model_class: DeclarativeMeta,
             storage_instance,
             **kwargs) -> Union[list, DeclarativeMeta]:
        tablename = model_class.__tablename__
        filename = storage_instance.schema[tablename].file
        cls = storage_instance._tbl_cls_from_tablename(tablename)
        with open((storage_instance.path / filename), "w") as fout:
            existing = json.load(fout)
            if kwargs:
                requested_column, requested_id = list(kwargs.items())
                rows = [d.get(requested_column) for d in existing]
                nr = rows.index(requested_id)
                item = existing[nr]
                return cls(**item)
            else:
                return [cls(**data) for data in existing]


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


@lru_cache
def get_controller(storage_class) -> Type[CrudInterface]:
    if isinstance(storage_class, Database):
        return SqlController
    elif isinstance(storage_class, JsonAdapter):
        return JsonController


__all__ = ["get_controller"]
