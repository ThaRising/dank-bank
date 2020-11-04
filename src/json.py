import json
from configparser import ConfigParser

from drizm_commons.sqla import Base, SQLAIntrospector
from drizm_commons.utils import get_application_root, Path


class JsonAdapter:
    def __init__(self) -> None:
        self.schema = ConfigParser()
        self.path = Path(get_application_root()) / ".json_db"
        if self.path.exists():
            self.path.rmdir()
        self.path.mkdir()

    def create(self) -> None:
        for t in Base.metadata.sorted_tables:
            table = SQLAIntrospector(t)
            filename = f"{table.tablename}.json"
            with open((self.path / filename), "w") as fout:
                json.dump([], fout)
            data = {
                "file": filename,
                "pk": table.primary_keys(),
                "uq": table.unique_keys(),
                "fk": table.foreign_keys()
            }
            self.schema[table.tablename] = data
        table_map = Path(self.path) / "tbl_map.ini"
        table_map.touch()
        with open(table_map, "w") as fout:
            self.schema.write(fout)

    def destroy(self):
        self.path.rmdir()
