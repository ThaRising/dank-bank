import pytest
from src.storage import get_storage, get_controller


@pytest.fixture(scope="session")
def get_sql_storage():
    db = get_storage("sql")
    db.create()
    yield db
    db.destroy()


@pytest.fixture(scope="session")
def get_sql_controller(get_sql_storage):
    controller = get_controller(get_sql_storage)
    yield controller
