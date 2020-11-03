from src import Storage

if __name__ == '__main__':
    db = Storage(
        "sql", conn_args_overrides={
            "dialect": "sqlite",
            "host": "data.sqlite3"
        }
    )
    db.create()
