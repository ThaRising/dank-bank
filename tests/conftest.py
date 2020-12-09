from typing import Literal

import pytest

from src.storage import Storage


@pytest.fixture(scope="session", params=["sql", "json"])
def storage(request) -> Storage:
    storage_type: Literal['sql', 'json'] = request.param

    # We can conveniently sneak in a test case right here
    with pytest.raises(RuntimeError):
        # This should fail as we have not previously
        # initialized the storage
        # for any of the supported storage types
        Storage()

    store = Storage(storage_type)
    store.db.create()

    yield store

    store.db.destroy()

    # We also need to reset the __interned cache after each run
    # Double underscore variables get namespace shifted
    # so we need to do a force lookup to find their new name
    attr_name = "__interned"
    cache_attr = [attr for attr in dir(Storage) if attr_name in attr][0]
    setattr(Storage, cache_attr, {})
