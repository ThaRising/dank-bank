import datetime
import decimal
from typing import Optional

import sqlalchemy as sqla
from drizm_commons.sqla import Base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship


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
