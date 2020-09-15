import sqlalchemy as sqla
from .storage.datastores.sql import Base


class Benutzer(Base):
    id = sqla.Column(sqla.Integer, primary_key=True)
    vorname = sqla.Column(sqla.String)
    nachname = sqla.Column(sqla.String)


__all__ = ["Benutzer"]
