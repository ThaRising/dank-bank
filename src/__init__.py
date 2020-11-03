from drizm_commons.sqla import Database

from . import models
from .controllers import get_controller
from .json import JsonAdapter


def get_storage(storage_type: str):
    if storage_type == "sql":
        return Database(dialect="sqlite")
    elif storage_type == "json":
        return JsonAdapter()


__all__ = ["get_storage", "get_controller", "models"]
