import json
from configparser import ConfigParser

from drizm_commons.sqla import Base, SQLAIntrospector
from drizm_commons.utils import get_application_root, Path


class JsonAdapter:
    def __init__(self) -> None:
        self.schema = ConfigParser()

        self.path = Path(get_application_root()) / ".json_db"
        self.table_map = Path(self.path) / "tbl_map.ini"

    def _load(self):
        with open(self.table_map, "r") as fin:
            self.schema.read_file(fin)

    def create(self) -> None:
        """ Create the JSON 'database' or schema """
        # If a table mapping already exists,
        # load it instead of deleting
        # if not create the folder for our 'json db'
        if self.path.exists():
            self._load()
            return
        self.path.mkdir()

        # goes through all declared tables
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

        # creates the file 'tbl_map.ini'
        # and dumps the content of self.schema into it
        self.table_map.touch()
        with open(self.table_map, "w") as fout:
            self.schema.write(fout)

    def destroy(self):
        """ Destroys the JSON 'database' """
        self.path.rmdir()
