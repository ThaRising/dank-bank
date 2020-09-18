from abc import ABC, abstractmethod
from ..interfaces import CrudInterface


class Datastore(CrudInterface, ABC):
    adapter: object

    @abstractmethod
    def create_database(self) -> None:
        pass

    @abstractmethod
    def destroy_database(self) -> None:
        pass


__all__ = ["Datastore"]
