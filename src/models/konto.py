import random
import string

from drizm_commons.sqla import Base

from src.storage.managers import BaseManager, ManagerMixin
import sqlalchemy as sqla


class Konto(ManagerMixin, Base):
    manager = BaseManager

    pk = None
    kontonummer = sqla.Column(sqla.String, primary_key=True)
    kontostand = sqla.Column(sqla.Integer)
    besitzer = sqla.Column(sqla.String, sqla.ForeignKey("kunde.pk"))
    waehrung = sqla.Column(sqla.String)

    def __init__(self, **kwargs) -> None:
        # generate 12-digit long mix,
        # of random uppercase letters and digits
        if kwargs.get("kontonummer"):
            self.kontonummer = kwargs.pop("kontonummer")
        else:
            self.kontonummer = "".join(
                random.choices((string.ascii_uppercase + string.digits), k=12)
            )

        if kwargs.get("kontostand"):
            self.kontostand = kwargs.pop("kontostand")
        else:
            self.kontostand = 0
        self.waehrung = "EUR"
        super(Konto, self).__init__(**kwargs)
