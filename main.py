from src.models import *
from src.storage.datastores.sql.sql import get_db
from src.storage.datastores.json.encoder import AlchemyEncoder
import json
from pathlib import Path


if __name__ == '__main__':
    b = Benutzer(vorname="Ben", nachname="Koch")
    with open(Path(__file__).parent / "hello.json", "a") as fout:
        json.dump(b, fout, cls=AlchemyEncoder)
