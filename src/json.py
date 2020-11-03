import json
import os
import shutil
from configparser import ConfigParser
from pathlib import Path
from typing import Any

from drizm_commons.inspect import SQLAIntrospector
from drizm_commons.sqla import Base
from sqlalchemy.ext.declarative import DeclarativeMeta


def is_dunder(name: str) -> bool:
    if name[:2] and name[-2:] in ("__",):
        return True
    return False


class AlchemyEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        # Check if the class is an SQLAlchemy table
        if isinstance(o.__class__, DeclarativeMeta):
            fields = {}
            # Get all columns of the table
            for field in [f for f in dir(o) if not is_dunder(f) and f != "metadata"]:
                # Obtain the value of the field
                data = getattr(o, field)
                try:  # Try JSON encoding the field, if it fails, skip the field
                    json.dumps(data)
                    fields[field] = data
                except TypeError:
                    pass  # TODO: implement edge cases here
            return fields

        # If it is not an SQLAlchemy table use the default encoder
        return super(AlchemyEncoder, self).default(o)


class JsonAdapter:
    def __init__(self) -> None:
        self.schema = ConfigParser()
        self.path = Path(os.environ.get("PYTHONPATH")) / ".json_db"
        if self.path.exists():
            self.destroy()

    def create(self) -> None:
        for table in Base.metadata.sorted_tables:
            t = SQLAIntrospector(table)
            data = {
                "file": f"{table.name}.json",
                "pk": t.primary_keys(),
                "uq": t.unique_keys(),
                "fk": t.foreign_keys()
            }
            self.schema[table.name] = data
        with open(Path(self.path) / "tbl_map.ini", "w") as fout:
            self.schema.write(fout)

    def destroy(self):
        shutil.rmtree(str(self.path))
