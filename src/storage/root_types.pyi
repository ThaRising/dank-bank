import typing
from typing import TypeVar

from drizm_commons.sqla import Database, Base

from src.storage.json import JsonAdapter
from src.storage.managers import sql, json
from src.storage.managers.mixin import ManagerMixin

ManagerT = TypeVar("ManagerT", sql.SqlManager, json.JsonManager)
StorageT = TypeVar("StorageT", JsonAdapter, Database)

AnyScalar = typing.Union[int, float, str]
Identifier = typing.Union[int, str]
StorageType = typing.Literal['sql', 'json']

class DatabaseObject(ManagerMixin, Base):
    ...
