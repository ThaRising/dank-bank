from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Union, Type

from drizm_commons.sqla import Base, Database
from sqlalchemy.ext.declarative import DeclarativeMeta

from . import Storage
from .json import JsonAdapter


class CrudInterface(ABC):
    def __init__(self,
                 model_instance: Base) -> None:
        self.model_instance = model_instance
        self.db = Storage()

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abstractmethod
    def delete(self, **kwargs) -> None:
        pass

    @abstractmethod  # noqa may not receive callable
    @staticmethod
    def read(model_class: DeclarativeMeta,
             **kwargs) -> Union[list, DeclarativeMeta]:
        pass


class JsonController(CrudInterface):
    def create(self):
        pass

    def update(self, *args, **kwargs):
        pass

    def delete(self, **kwargs) -> None:
        pass

    @staticmethod
    def read(model_class: DeclarativeMeta,
             **kwargs) -> Union[list, DeclarativeMeta]:
        pass


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
             **kwargs) -> Union[list, DeclarativeMeta]:
        db = Storage()
        if not kwargs:
            with db.Session() as sess:
                return sess.query(model_class).all()
        with db.Session() as sess:
            return sess.query(model_class).filter_by(**kwargs).all()


@lru_cache
def get_controller() -> Type[CrudInterface]:
    storage_class = Storage()
    if isinstance(storage_class, Database):
        return SqlController
    elif isinstance(storage_class, JsonAdapter):
        return JsonController


__all__ = ["get_controller"]
