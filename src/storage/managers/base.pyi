from abc import ABC
from typing import overload, Generic, Dict, Any, List

from sqlalchemy.ext.declarative import DeclarativeMeta

from src.storage.root_types import ManagerT, AnyScalar, Identifier, StorageType


class BaseManagerInterface(ABC, Generic[ManagerT]):
    klass: DeclarativeMeta
    db: ManagerT
    db_type: StorageType

    def __init__(self,
                 klass: DeclarativeMeta,
                 storage: ManagerT,
                 store_type: StorageType
                 ) -> None:
        ...

    def _is_static(self) -> bool: ...

    def save(self) -> None: ...

    def update(self, data: Dict[str, Any]) -> DeclarativeMeta: ...

    def delete(self, **kwargs: AnyScalar) -> None: ...

    @overload
    def read(self,
             unique_identifier: Identifier
             ) -> DeclarativeMeta:
        ...

    @overload
    def read(self, **kwargs: AnyScalar) -> List[DeclarativeMeta]: ...

    def all(self) -> List[DeclarativeMeta]: ...


class AbstractManager(BaseManagerInterface):
    ...


class BaseManager(AbstractManager):
    ...
