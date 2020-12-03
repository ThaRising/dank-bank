from typing import Optional, Type, Literal


class Storage:
    __interned = {}

    def __new__(cls,
                storage_type: Optional[Literal['sql', 'json']] = None
                ) -> "Storage":
        # We do all imports inside of the methods scope,
        # to avoid circular dependencies since we import this
        # module from across the board in the package
        from .json import JsonAdapter
        from drizm_commons.sqla import Database

        STORAGE_TYPES = {
            "sql": lambda: Database(
                dialect="sqlite",
                host="data.sqlite3",
            ),
            "json": lambda: JsonAdapter()
        }

        from .managers.sql import SqlManager
        from .managers.json import JsonManager
        MANAGER_TYPES = {
            "sql": SqlManager,
            "json": JsonManager
        }

        # if no storage_type has explicitly been passed, attempt to return
        # the saved default implementation
        if not storage_type:
            try:
                return cls.__interned[None]
            except KeyError:
                raise RuntimeError(
                    f"Class Storage ({cls.__name__}) still awaiting initialization. "
                    "You may have called storage related code, or created a model instance "
                    "before initializing this class."
                )

        # If we do have a provided type, check if it is valid
        # and initialize the database from that
        try:
            db = STORAGE_TYPES[storage_type]
            db = db()

            # managers get initialized dynamically,
            # with either a class object or class instance
            # by the hybrid_property on the respective Model classes
            manager = MANAGER_TYPES[storage_type]

        except KeyError:
            raise ValueError(
                f"Value '{storage_type}' is not a valid identifier for "
                f"a storage type, must be one of {STORAGE_TYPES.keys()}"
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
