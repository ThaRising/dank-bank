import datetime

from src.storage import get_storage, get_controller
from src.storage.models import Kunde

if __name__ == '__main__':
    db = get_storage("sql")
    db.create()
    k = Kunde(
        name="Ben Koch",
        adresse="fgr rgtert ergert ergtert",
        geb_date=datetime.date.today()
    )
    c = get_controller(db)
    C = c(k, db)
    C.create()
    c.read(Kunde, db, pk=k.pk)
