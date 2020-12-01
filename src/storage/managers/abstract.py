from abc import ABC, abstractmethod
from typing import Union

from drizm_commons.sqla import Base
from sqlalchemy.ext.declarative import DeclarativeMeta


class CrudInterface(ABC):
    def __init__(self, model_instance: Base) -> None:
        self.model_instance = model_instance

        from . import get_storage
        self.db = get_storage()

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abstractmethod
    def delete(self, **kwargs) -> None:
        pass

    @staticmethod
    def read(model_class: DeclarativeMeta,
             *args, **kwargs) -> Union[list, DeclarativeMeta]:
        pass
