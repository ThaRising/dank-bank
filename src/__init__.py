from typing import Union, Optional

from drizm_commons.sqla import Database

from . import models
from .interfaces import get_controller
from .json import JsonAdapter


class Storage:
    __state = None

    def __new__(cls, /,
                storage_type: str = None,
                *, conn_args_overrides: Optional[dict] = None
                ) -> Union[Database, JsonAdapter]:
        if cls.__state:
            return cls.__state
        if not storage_type:
            raise ValueError("storage_type parameter is required")

        if storage_type == "sql":
            if conn_args_overrides:
                cls.__state = Database(conn_args=conn_args_overrides)
            cls.__state = Database(dialect="sqlite")
        elif storage_type == "json":
            cls.__state = JsonAdapter()
        else:
            raise TypeError(f"storage_type {storage_type} not supported")
        return cls.__state


__all__ = ["Storage", "get_controller", "models"]
