import datetime
import uuid
from typing import Union

from dateutil.relativedelta import relativedelta
from drizm_commons.sqla import Base
from sqlalchemy.orm import validates

from ..managers import BaseManager, ManagerMixin
import sqlalchemy as sqla


class Kunde(ManagerMixin, Base):
    manager = BaseManager

    pk = sqla.Column(sqla.String, primary_key=True)
    name = sqla.Column(sqla.String)
    strasse = sqla.Column(sqla.String(100))
    stadt = sqla.Column(sqla.String)
    plz = sqla.Column(sqla.String)
    geb_date = sqla.Column(sqla.Date)

    def __init__(self, **kwargs) -> None:
        self.pk = uuid.uuid4().hex
        super(Kunde, self).__init__(**kwargs)

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

        # shortest possible street name would be sth like 'aweg 1'
        assert len(strasse) >= 6

        return strasse

    @validates("stadt")
    def validate_stadt(self, _, stadt: str) -> str:
        assert len(stadt) >= 2

        return stadt

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

        # subtract 18 years from today to validate min required age
        min_date = current_date - relativedelta(years=18)
        assert geb_date < min_date

        return geb_date

    @property
    def konten(self):
        from .konto import Konto
        return Konto.objects.read(Konto, besitzer=self.pk)
