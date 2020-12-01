import datetime

from src.storage import Storage
from src.storage.models import Kunde


if __name__ == '__main__':
    Storage("sql")
    kunde = Kunde(
        name="Ben Koch",
        plz="16386",
        stadt="Berlin",
        strasse="fgr rgtert ergert ergtert",
        geb_date=datetime.date(2000, 1, 1)
    )
    kunde.objects.save()
    print(kunde.objects.all())
    print(Kunde.objects.all())
