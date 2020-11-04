import datetime

from src import get_storage, get_controller
from src.models import Kunde

if __name__ == '__main__':
    db = get_storage("json")
    db.create()
    k = Kunde(
        name="Ben Koch",
        adresse="iubuhbijgkijnkjn",
        geb_date=datetime.date.today()
    )
    c = get_controller(db)
    C = c(k, db)
    C.create()
    c.read(Kunde, db, pk=k.pk)
