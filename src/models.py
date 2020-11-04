import sqlalchemy as sqla
from drizm_commons.sqla import Base
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import relationship, validates
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
