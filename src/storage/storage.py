from typing import Optional, Type


class Storage:
    __interned = {}

    db: Type[object]
    manager: Type[object]

    def __new__(cls,
                storage_type: Optional[str] = None) -> "Storage":
        # We import inside of the methods scope to avoid circular dependencies
        from .json import JsonAdapter
        from drizm_commons.sqla import Database

        STORAGE_TYPES = {
            "sql": lambda: Database(
                dialect="sqlite",
                host="data.sqlite3",
            ),
            "json": lambda: JsonAdapter()
        }

        MANAGER_TYPES = {
            "sql": None,
            "json": None
        }

        # if no storage_type has explicitly been passed, attempt to return
        # the saved default implementation
        if not storage_type:
            try:
                return cls.__interned[None]
            except KeyError:
                raise NameError(
                    f"Class Storage ({cls.__name__}) still awaiting initialization."
                )

        # If we do have a provided type, check if it is valid
        # and initialize the database from that
        try:
            db = STORAGE_TYPES[storage_type]
            db = db()
            manager = MANAGER_TYPES[storage_type]
        except KeyError:
            raise ValueError(
                f"Value '{storage_type}' is not a valid identifier for "
                f"a storage type, must be one of {[t for t in STORAGE_TYPES.keys()]}"
            )

        # if this is the first initialization, we set this storage as default
        if not cls.__interned or not cls.__interned[storage_type]:
            obj = super().__new__(cls)
            obj.db = db
            obj.manager = manager

            if not cls.__interned:
                cls.__interned[None] = obj
            cls.__interned[storage_type] = obj

        return cls.__interned[storage_type]
