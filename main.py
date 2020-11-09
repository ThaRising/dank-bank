import datetime

from src.storage import get_storage, get_controller
from src.storage.models import Kunde, Konto

if __name__ == '__main__':
    db = get_storage("sql")
    db.create()
    controller = get_controller(db)
    kunde = Kunde(
        name="Ben Koch",
        plz="16386",
        stadt="Berlin",
        strasse="fgr rgtert ergert ergtert",
        geb_date=datetime.date(2000, 1, 1)
    )
    kunde_controller = controller(kunde, db)
    kunde_controller.create()
    kunde_controller.read(Kunde, db, pk=kunde.pk)
