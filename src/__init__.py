from functools import lru_cache
from typing import Type

from drizm_commons.sqla import Database

from . import controllers
from . import models
from .abstract import CrudInterface
from .json import JsonAdapter


@lru_cache
def get_storage(storage_type: str):
    if storage_type == "sql":
        return Database(
            dialect="sqlite",
            host="data.sqlite3"
        )
    elif storage_type == "json":
        return JsonAdapter()


@lru_cache
def get_controller(storage_class) -> Type[CrudInterface]:
    if isinstance(storage_class, Database):
        return controllers.SqlController
    elif isinstance(storage_class, JsonAdapter):
        return controllers.JsonController


__all__ = ["get_storage", "get_controller", "models"]
