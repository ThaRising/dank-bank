import typing
from typing import Dict, Optional, Type
from src.storage.root_types import StorageType, ManagerT, StorageT

class Storage:
    __interned: typing.ClassVar[Dict[StorageType, Storage]]

    db: StorageT
    manager: Type[ManagerT]
    def __new__(cls, storage_type: Optional[StorageType] = None) -> Storage: ...
