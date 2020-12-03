from typing import TypeVar

import typing

from src.storage.managers import sql, json

from src.storage.json import JsonAdapter
from drizm_commons.sqla import Database

ManagerT = TypeVar("ManagerT", sql.SqlManager, json.JsonManager)
StorageT = TypeVar("StorageT", JsonAdapter, Database)

AnyScalar = typing.Union[int, float, str]
Identifier = typing.Union[int, str]
StorageType = typing.Literal['sql', 'json']
