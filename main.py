import datetime

from src.storage import get_storage, get_controller
from src.storage.models import Kunde, Konto

if __name__ == '__main__':
    db = get_storage("json")
    db.create()
    Controller = get_controller(db)
    kunde = Kunde(
        name="Ben Koch",
        plz="16386",
        stadt="Berlin",
        strasse="fgr rgtert ergert ergtert",
        geb_date=datetime.date(2000, 1, 1)
    )
    kunde_controller = Controller(kunde)
    kunde_controller.create()
    konto = Konto(
        besitzer=kunde.pk
    )
    konto_controller = Controller(konto)
    konto_controller.create()
    print(kunde.konten)

    Storage("json")
    kunde = Kunde(
        name="Ben Koch",
        plz="16386",
        stadt="Berlin",
        strasse="fgr rgtert ergert ergtert",
        geb_date=datetime.date(2000, 1, 1)
    )
    kunde.objects.save()
