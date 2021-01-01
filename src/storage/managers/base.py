from abc import ABC, abstractmethod
from inspect import isclass

from drizm_commons.inspect import SQLAIntrospector
from drizm_commons.testing.truthiness import is_dunder
from drizm_commons.utils import decorate_class_object_methods
from drizm_commons.utils.decorators import resolve_super_auto_resolution


class BaseManagerInterface(ABC):
    def __init__(self, klass, storage, store_type):
        self.klass = klass
        self.db = storage

        # This value gives subclasses a way to execute
        # different code based on the type of storage we are using.
        # Manager classes can also manually specify this as a class attribute.
        self.db_type = store_type or self.__class__.db_type

    def _is_static(self) -> bool:
        """ Check whether this manager is serving an instance or a class """
        if isclass(self.klass):
            return True
        return False

    def _get_identifier_column_name(self):
        """ Get the name of the primary key column """
        primary_keys = SQLAIntrospector(self.klass).primary_keys()
        if len(primary_keys) > 1:
            raise TypeError(
                "Composite-Primary Keys are not supported by this Manager"
            )
        return primary_keys[0]

    def _get_identifier(self):
        """ Get the value of the primary key column """
        return getattr(
            self.klass, self._get_identifier_column_name()
        )

    @abstractmethod
    def save(self):
        """
        Saves the current object to the database.

        This can be used both to save a new object to the database
        and to update an existing object.
        """
        pass

    @abstractmethod
    def delete(self):
        """
        Remove the current object from the database.
        """
        pass

    @abstractmethod
    def get(self, identifier):
        """
        Retrieve an instance by its primary key.

        If no matching object is found,
        a src.storage.exc.ObjectNotFound exception is raised.
        """
        pass

    @abstractmethod
    def filter(self, **kwargs):
        """
        Do exact and case sensitive filtering,
        based on provided kwargs.

        This will never throw an error and instead simply return an empty list,
        if no matching entities could be found.
        """
        pass

    @abstractmethod
    def all(self):
        """
        Syntactic / Semantic sugar for querying all entities of a Model.
        """
        pass


class AbstractManager:
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

    def __new__(cls, klass, storage_type=None):
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
        Manager = decorate_class_object_methods(
            Manager, resolve_super_auto_resolution
        )

        return Manager(klass, db, storage_name)


class BaseManager(AbstractManager):
    """ Will return the default manager for the current storage type """
    pass
