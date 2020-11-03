from src import get_storage

if __name__ == '__main__':
    """
    db = Storage(
        "sql", conn_args_overrides={
            "dialect": "sqlite",
            "host": "data.sqlite3"
        }
    )
    """
    db = get_storage("json")
    db.create()
