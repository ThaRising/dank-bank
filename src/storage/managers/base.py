from abc import ABC, abstractmethod
from inspect import isclass
from typing import Optional, Union, Type


class BaseManagerInterface(ABC):
    def __init__(self, klass, storage):
        self.klass = klass
        self.db = storage

    def _is_static(self) -> bool:
        """ Check whether this manager is serving an instance or a class """
        if isclass(self.klass):
            return True
        return False

    @abstractmethod
    def save(self) -> None:
        pass

    @abstractmethod
    def update(self, *args, **kwargs) -> Type[object]:
        pass

    @abstractmethod
    def delete(self, **kwargs) -> None:
        pass

    @abstractmethod
    def read(self, *args, **kwargs) -> Union[list, Type[object]]:
        pass

    def all(self):
        return self.read()


def BaseManager(klass, storage_type: Optional[str] = None):
    from ..storage import Storage
    if not storage_type:
        storage = Storage()
    else:
        storage = Storage(storage_type)

    return storage.manager(klass, storage.db)
