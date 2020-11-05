from typing import Union

import sqlalchemy as sqla
from drizm_commons.sqla import Base
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import relationship, validates
import uuid
import datetime


class Kunde(Base):
    pk = sqla.Column(
        sqla.String,
        default=uuid.uuid4().hex,
        primary_key=True
    )
    name = sqla.Column(sqla.String)
    strasse = sqla.Column(sqla.String(100))
    stadt = sqla.Column(sqla.String)
    plz = sqla.Column(sqla.String)
    geb_date = sqla.Column(sqla.Date)
    konten = relationship("Konto")

    @validates("name")
    def validate_name(self, _, name) -> str:
        # make sure we have at least 2 word-blocks in our input
        assert len(name.split()) >= 2

        # shortest possible name should be 4-chars + 1 whitespace
        assert len(name) >= 5

        # no numbers should be allowed in a name
        letter_is_num = [
            letter.isdigit() for letter in name.replace(" ", "")
        ]
        assert not any(letter_is_num)

        return name

    @validates("strasse")
    def validate_adresse(self, _, strasse: str) -> str:
        # address structure should be '<street-name> <street> <number>'
        # the <street> part is optional, so 2 blocks or more
        street_blocks = strasse.split()
        assert len(street_blocks) >= 2

        # checks shortest possible street name length 'aweg 1'
        assert len(strasse) >= 6

        return strasse


    @validates("stadt")
    def validate_stadt(self, _, stadt: str) -> str:
        assert len(stadt) >= 2

        return stadt#

    @validates("plz")
    def validates_plz(self, _, plz: str) -> str:
        # German only postal codes
        assert len(plz) == 5

        return plz

    @validates("geb_date")
    def validate_geb_date(self, _,
                          geb_date: Union[str, datetime.date]
                          ) -> datetime.date:
        # in case the user passes a isoformat date string
        # convert it to a date instance
        # isoformat date string e.g. '2020-11-05'
        if isinstance(geb_date, str):
            date_parts = geb_date.split("-")
            date_parts = [int(i) for i in date_parts]
            geb_date = datetime.date(*date_parts)

        # get current date for comparison to validate age
        current_date = datetime.date.today()

        # subtract 18 years from today to check age
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
