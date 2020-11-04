import sqlalchemy as sqla
from drizm_commons.sqla import Base
from sqlalchemy.orm import relationship
import uuid


class Kunde(Base):
    pk = sqla.Column(
        sqla.String,
        default=uuid.uuid4().hex,
        primary_key=True
    )
    name = sqla.Column(sqla.String)
    adresse = sqla.Column(sqla.String)
    geb_date = sqla.Column(sqla.Date)
    konten = relationship("Konto")


class Konto(Base):
    pk = None
    kontonummer = sqla.Column(sqla.String, primary_key=True)
    kontostand = sqla.Column(sqla.Integer)
    besitzer = sqla.Column(
        sqla.String,
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


class Waehrung(Base):
    pk = None
    code = sqla.Column(sqla.String, primary_key=True)
    konten = relationship("Konto")


__all__ = ["Kunde", "Konto", "Waehrung"]
