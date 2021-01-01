import datetime
import uuid
from typing import Union, Optional

import bcrypt
import sqlalchemy as sqla
from dateutil.relativedelta import relativedelta
from drizm_commons.sqla import Base
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import validates

from src.storage.managers import ManagerMixin, AbstractManager


class KundenManager(AbstractManager):
    # noinspection PyMethodMayBeStatic
    def hash_password(self, cleartext_password: str) -> str:
        return bcrypt.hashpw(
            cleartext_password.encode(),
            bcrypt.gensalt()
        ).decode("utf-8")

    # noinspection PyMethodMayBeStatic
    def is_password_valid(self,
                          cleartext_password: str,
                          hashed_password: str) -> bool:
        return bcrypt.checkpw(
            cleartext_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    def login_user(self,
                   username: str,
                   password: str) -> Optional[DeclarativeMeta]:
        """
        Return a user object if the provided credentials are valid,
        otherwise return None
        """
        user = self.filter(username=username)
        if len(user) > 1:
            raise RuntimeError(
                "Critical error, duplicate users in database."
            )
        elif len(user) == 0:
            return None
        user = user[0]
        if self.is_password_valid(
            password, user.password
        ):
            return user
        return None

    def delete(self) -> None:
        for konto in self.klass.konten:
            konto.objects.delete()

        super().delete()


class Kunde(ManagerMixin, Base):
    manager = KundenManager

    pk = sqla.Column(sqla.String, primary_key=True)

    username = sqla.Column(sqla.String, unique=True)
    password = sqla.Column(sqla.String)

    name = sqla.Column(sqla.String)
    strasse = sqla.Column(sqla.String(100))
    stadt = sqla.Column(sqla.String)
    plz = sqla.Column(sqla.String)
    geb_date = sqla.Column(sqla.Date)

    def __init__(self, **kwargs) -> None:
        if kwargs.get("pk"):
            pk = kwargs.pop("pk")
        else:
            pk = uuid.uuid4().hex
        self.pk = pk
        super(Kunde, self).__init__(**kwargs)

    @validates("username")
    def validate_username(self, _, username) -> str:
        assert len(username) >= 5, "Das Username muss mind. 5 Zeichen enthalten."

        return username

    @validates("password")
    def validate_password(self, _, password) -> str:
        assert len(password) >= 3, "Passwort muss mind. 3 Zeichen lang sein."

        assert not password.isnumeric(), ("Das Passwort muss sowohl Buchstaben, "
                                          "als auch Zahlen enthalten.")
        assert not password.isalpha(), ("Das Passwort muss sowohl Buchstaben, "
                                        "als auch Zahlen enthalten.")

        return password

    @validates("name")
    def validate_name(self, _, name) -> str:
        # make sure we have at least 2 word-blocks in our input
        assert len(name.split()) >= 2, "Name muss mindestens aus Vor und Nachname bestehen."

        # shortest possible name should be 4-chars + 1 whitespace
        assert len(name) >= 5, ("Name muss mindestens 5 Zeichen lang sein "
                                "(4 Zeichen + 1 Leerzeile).")

        # no numbers should be allowed in a name
        letter_is_num = [
            letter.isdigit() for letter in name.replace(" ", "")
        ]
        assert not any(letter_is_num), "Name kann keine Zahlen enthalten."

        return name

    @validates("strasse")
    def validate_adresse(self, _, strasse: str) -> str:
        # address structure should be '<street-name> <street> <number>'
        # the <street> part is optional, so 2 blocks or more
        street_blocks = strasse.split()
        assert len(street_blocks) >= 2, ("Straße muss mind. aus einem Straßennamen "
                                         "und einer Hausnummer bestehen.")

        # shortest possible street name would be sth like 'aweg 1'
        assert len(strasse) >= 6, ("Straße muss mind. 4 Zeichen haben"
                                   " und ein Leerzeichen + Hausnummer.")

        return strasse

    @validates("stadt")
    def validate_stadt(self, _, stadt: str) -> str:
        assert len(stadt) >= 2, "Stadtname muss mind. 2 Zeichen haben."

        return stadt

    @validates("plz")
    def validates_plz(self, _, plz: str) -> str:
        # German only postal codes
        assert len(plz) == 5, "Muss mind. 5 Zeichen haben."

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
        assert geb_date < min_date, "Sie müssen mind. 18 Jahre alt sein."

        return geb_date

    @property
    def konten(self):
        from .konto import Konto
        return Konto.objects.filter(besitzer=self.pk)
