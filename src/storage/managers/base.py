from abc import ABC, abstractmethod
from inspect import isclass
from typing import Optional, Union, Type, TypeVar, List

from drizm_commons.utils import is_dunder
from sqlalchemy.ext.declarative import DeclarativeMeta

DeclarativeSubtype = TypeVar("DeclarativeSubtype", bound=DeclarativeMeta)


class BaseManagerInterface(ABC):
    def __init__(self, klass, storage, store_type: str):
        self.klass = klass
        self.db = storage

        # This value gives subclasses a way to execute
        # different code based on the type of storage we are using
        self.db_type = store_type

    def _is_static(self) -> bool:
        """ Check whether this manager is serving an instance or a class """
        if isclass(self.klass):
            return True
        return False

    @abstractmethod
    def save(self) -> None:
        pass

    @abstractmethod
    def update(self, data: dict) -> DeclarativeSubtype:
        pass

    @abstractmethod
    def delete(self, **kwargs) -> None:
        pass

    @abstractmethod
    def read(self, *args, **kwargs) -> Union[list, DeclarativeSubtype]:
        """
        Will take either one positional argument or n-keyword arguments.

        When a positional argument is provided it is assumed to be
        the primary key of the object.
        If this lookup fails this method will throw an error.

        When keyword arguments are provided,
        filtering will occur based on the provided parameters and their values.
        This will never throw an error and instead simply return an empty list,
        if no matching entities could be found.
        """
        pass

    def all(self) -> List[DeclarativeSubtype]:
        """
        Syntactic / Semantic sugar for querying all entities of a Model.
        """
        return self.read()


ManagerT = TypeVar("ManagerT", bound=BaseManagerInterface)


class AbstractManager(ManagerT):
    """
    Class that serves as a factory for Manager classes.

    By default it will output the default Manager class,
    for the selected storage type.

    If the user subclasses this class then they can add their own
    functionality to the manager and this class will automatically
    merge both class namespaces together.

    This means the product will be the base of the automatically
    selected Manager with the addition of the user specified Methods.
    """
    klass: DeclarativeSubtype

    def __new__(cls, klass, storage_type: Optional[str] = None):
        from ..storage import Storage
        from drizm_commons.sqla import Database

        if not storage_type:
            storage = Storage()
        else:
            storage = Storage(storage_type)

        db = storage.db
        if isinstance(db, Database):
            storage_name = "sql"
        else:
            storage_name = "json"

        # Manually merge the class namespaces
        # of our selected default manager class, e.g. SqlManager
        # and the overriding Manager class the user defined
        Manager = type(
            cls.__name__,
            (storage.manager,),
            {
                attr: getattr(
                    cls, attr
                ) for attr in dir(cls) if not is_dunder(attr)
            }
        )

        return Manager(klass, db, storage_name)  # type: Type[BaseManagerInterface]

    def _is_static(self) -> bool: ...

    def save(self) -> None: ...

    def update(self, data: dict) -> Type[DeclarativeSubtype]: ...

    def delete(self, **kwargs) -> None: ...

    def read(self, *args, **kwargs) -> Union[list, DeclarativeSubtype]: ...

    def all(self) -> List[DeclarativeSubtype]: ...


class BaseManager(AbstractManager):
    """ Will return the default manager for the current storage type """
    pass
