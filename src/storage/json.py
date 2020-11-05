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
        """ Create the JSON 'database' or schema """
        # goes through all tables
        for t in Base.metadata.sorted_tables:
            # inspect the table
            table = SQLAIntrospector(t)
            filename = f"{table.tablename}.json"
            with open((self.path / filename), "w") as fout:
                json.dump([], fout)
            # declares the schema for the table
            data = {
                "file": filename,
                "pk": table.primary_keys(),
                "uq": table.unique_keys(),
                "fk": table.foreign_keys()
            }
            self.schema[table.tablename] = data

        # creates the file 'tbl_map.ini '
        # and dumps the content of self.schema into it
        table_map = Path(self.path) / "tbl_map.ini"
        table_map.touch()
        with open(table_map, "w") as fout:
            self.schema.write(fout)

    def destroy(self):
        """ Destroys the JSON 'database' """
        self.path.rmdir()
