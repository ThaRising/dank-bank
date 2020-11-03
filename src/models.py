import datetime
import decimal
from typing import Optional

import sqlalchemy as sqla
from drizm_commons.sqla import Base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates
from dateutil.relativedelta import relativedelta


class Kunde(Base):
    name = sqla.Column(sqla.String)
    adresse = sqla.Column(sqla.String)
    geb_date = sqla.Column(sqla.Date)
    konten = relationship("Konto")

    def __init__(self,
                 name: str,
                 adresse: str,
                 geb_date: datetime.date) -> None:
        self.name = name
        self.adresse = adresse
        self.geb_date = geb_date

    @validates("name")
    def validate_name(self, key, name):
        assert len(name.split()) >= 2
        assert len(name) >= 5
        test = [l.isdigit() for l in name.replace(" ", "")]
        assert not any(test)
        return name

    @validates("adresse")
    def validate_adresse(self, key, adresse):
        assert len(adresse.split()) >= 3
        assert len(adresse) >= 10
        assert len(adresse) <= 150
        return adresse

    @validates("geb_date")
    def validate_geb_date(self, key, geb_date):
        assert isinstance(geb_date, datetime.date)

        current_date = datetime.datetime.now().date()
        min_date = current_date - relativedelta(years=18)
        assert geb_date < min_date
        return geb_date


class Konto(Base):
    pk = None
    kontonummer = sqla.Column(sqla.String, primary_key=True)
    _kontostand_num = sqla.Column(sqla.Integer)
    _kontostand_dec = sqla.Column(sqla.Integer)
    besitzer = sqla.Column(
        sqla.Integer,
        sqla.ForeignKey(
            "kunde.pk"
        )
    )
    waehrung = sqla.Column(
        sqla.String,
        sqla.ForeignKey(
            "waehrung.code"
        )
    )

    def __init__(self, *,
                 besitzer: int,
                 waehrung: str,
                 kontostand: Optional[decimal.Decimal] = None,
                 ) -> None:
        self.besitzer_id = besitzer
        self.waehrung_code = waehrung
        self.kontostand = kontostand or decimal.Decimal(0)

    @hybrid_property
    def kontostand(self) -> decimal.Decimal:
        return decimal.Decimal(
            f"{self._kontostand_num}.{self._kontostand_dec}"
        )

    @kontostand.setter
    def kontostand(self, summe: decimal.Decimal) -> None:
        num, dec = str(summe).split(".")
        self._kontostand_num = num
        self._kontostand_dec = dec


class Waehrung(Base):
    pk = None
    code = sqla.Column(sqla.String, primary_key=True)
    konten = relationship("Konto")

    def __init__(self, code: str) -> None:
        self.code = code


__all__ = ["Kunde", "Konto", "Waehrung"]
