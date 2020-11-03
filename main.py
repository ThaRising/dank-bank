import datetime
import decimal
from abc import ABC, abstractmethod
from typing import Any, Union
from typing import Optional

from drizm_commons.sqla import Database


class CrudInterface(ABC):
    model: Any
    db: Any

    @abstractmethod
    def create(self, *args, **kwargs):
        pass

    def read(self, **kwargs) -> Union[list, "model"]:
        with self.db.Session() as sess:
            if kwargs:
                return sess.query(self.model).get(**kwargs)
            else:
                sess.query(self.model).all()

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    def delete(self, **kwargs) -> None:
        with self.db.Session() as sess:
            elem = sess.query(self.model).get(**kwargs)
            sess.delete(elem)


db = Database(
    dialect="sqlite",
    host="data.sqlite3"
)


class KundeController(CrudInterface):
    model = Kunde
    db = db

    def create(self, *,
               name: str,
               adresse: str,
               geb_date: datetime.date) -> Any:
        elem = self.model(
            name=name,
            adresse=adresse,
            geb_date=geb_date
        )
        with self.db.Session() as sess:
            sess.add(elem)
            return elem

    def update(self, pk: int, *,
               name: Optional[str] = None,
               adresse: Optional[str] = None):
        kwargs = locals()
        pk = kwargs.pop("pk")
        with self.db.Session() as sess:
            elem = self.read(pk=pk)
            for k, v in kwargs.items():
                setattr(elem, k, v)

    def add_konto(self, pk: int, konto):
        with self.db.Session() as sess:
            elem = sess.query(self.model).get(pk=pk)
            elem.konten += [konto]

    def remove_konto(self, pk: int, konto):
        with self.db.Session() as sess:
            elem = sess.query(self.model).get(pk=pk)
            elem.konten -= [konto]


class KontoController(CrudInterface):
    model = Konto
    db = db

    def create(self, *,
               kontonummer: str,
               kontostand: decimal.Decimal,
               besitzer: int,
               waehrung: str):
        kontostand, kontostand_dec = [int(i) for i in str(kontostand).split(".")]
        with self.db.Session() as sess:
            w = sess.query(Waehrung).get(code=waehrung)
            b = sess.query(Kunde).get(pk=besitzer)
            elem = self.model(
                kontonummer=kontonummer,
                kontostand=kontostand,
                kontostand_dec=kontostand_dec,
                waehrung=w,
                besitzer=b
            )
            sess.add(elem)
            return elem

    def update(self, kontonr: str, *,
               kontostand: decimal.Decimal):
        kontostand, kontostand_dec = [int(i) for i in str(kontostand).split(".")]
        with self.db.Session():
            elem = self.read(kontonummer=kontonr)
            elem.kontostand = kontostand
            elem.kontostand_dec = kontostand_dec


class WaehrungController(CrudInterface):
    model = Waehrung
    db = db

    def create(self, *,
               code: str):
        elem = self.model(
            code=code
        )
        with self.db.Session() as sess:
            sess.add(elem)
            return elem

    def update(self, *args, **kwargs):
        pass


if __name__ == '__main__':
    db.create()
    horst = KundeController().create(
        name="Horst Walther",
        adresse="iujogthjhgbxdukjfgbdejbvujhkbvreh",
        geb_date=datetime.date.today()
    )
    euro = WaehrungController().create(
        code="EUR"
    )
    KontoController().create(
        kontonummer="xghjh",
        kontostand=decimal.Decimal("25.89"),
        besitzer=horst.pk,
        waehrung=euro.code
    )
    db.destroy()
