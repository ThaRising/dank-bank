from functools import lru_cache
from drizm_commons.sqla import Database


@lru_cache
def get_data_storage(storage_type: str):
    if storage_type == "sql":
        return Database(
            dialect="sqlite"
        )
    elif storage_type == "json":
        return object


__all__ = ["get_data_storage"]
