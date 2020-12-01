from abc import ABC, abstractmethod
from inspect import isclass
from typing import Optional, Union, Type


class BaseManagerInterface(ABC):
    def __init__(self,
                 klass, *,
                 storage_type: Optional[str] = None) -> None:
        # We accept both instances and class objects
        self.klass = klass

    def _is_static(self) -> bool:
        """ Check whether this manager is serving an instance or a class """
        if isclass(self.klass):
            return True
        return False

    @abstractmethod
    def _get_storage(self):
        pass

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
    def read(*args, **kwargs) -> Union[list, Type[object]]:
        pass
