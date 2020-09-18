from abc import ABC, abstractmethod
from typing import Iterable


class CrudInterface(ABC):
    @abstractmethod
    def create(self, obj: object) -> None:
        pass

    @abstractmethod
    def read(self, tablename: str) -> list:
        pass

    @abstractmethod
    def retrieve(self, tablename: str, pks: Iterable) -> dict:
        pass

    @abstractmethod
    def update(self, tablename: str, pks: Iterable, obj: object):
        pass

    @abstractmethod
    def delete(self, tablename: str, pks: Iterable) -> None:
        pass
