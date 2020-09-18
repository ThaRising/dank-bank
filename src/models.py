import sqlalchemy as sqla
from .storage.sql import Base


class Benutzer(Base):
    id = sqla.Column(sqla.Integer, primary_key=True)
    vorname = sqla.Column(sqla.String)
    nachname = sqla.Column(sqla.String)


class TestTable(Base):
    name = sqla.Column(sqla.String, primary_key=True)
    sth = sqla.Column(sqla.Integer)


__all__ = ["Benutzer"]
