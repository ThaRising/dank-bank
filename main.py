from pathlib import Path

from src.models import *
from src.storage.json.datastore import JsonDatastore

if __name__ == '__main__':
    b = Benutzer(id=1, vorname="Ben", nachname="Koch")
    j = JsonDatastore(Path(__file__).parent / "data")
    j.create_database()
    j.create(b)
    print(j.read("benutzer"))
    print(j.retrieve("benutzer", [1]))
    j.destroy_database()
