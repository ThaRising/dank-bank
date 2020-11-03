import json
from sqlalchemy.ext.declarative import DeclarativeMeta
from typing import Any


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
