from abc import ABC
from typing import Generic, List, Optional, TypeVar, ClassVar

from sqlalchemy.ext.declarative import DeclarativeMeta

from src.storage.root_types import (
    ManagerT,
    AnyScalar,
    Identifier,
    StorageType,
    DatabaseObject,
)

class BaseManagerInterface(ABC, Generic[ManagerT]):
    klass: DatabaseObject
    db: ManagerT
    db_type: Optional[ClassVar[StorageType]]
    db_type: StorageType
    def __init__(
        self, klass: DatabaseObject, storage: ManagerT, store_type: StorageType
    ) -> None: ...
    def _is_static(self) -> bool: ...
    def _get_identifier_column_name(self) -> str: ...
    def _get_identifier(self) -> Identifier: ...
    def save(self) -> None: ...
    def delete(self) -> None: ...
    def get(self, identifier: Identifier) -> DatabaseObject: ...
    def filter(self, **kwargs: AnyScalar) -> List[DatabaseObject]: ...
    def all(self) -> List[DatabaseObject]: ...

T = TypeVar("T", bound=BaseManagerInterface)

class AbstractManager(T):
    def __new__(
        cls, klass: DeclarativeMeta, storage_type: Optional[StorageType] = None
    ) -> BaseManagerInterface: ...

class BaseManager(AbstractManager): ...
