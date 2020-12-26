import sqlalchemy.exc
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta

from .base import BaseManagerInterface
from ..exc import ObjectNotFound, ObjectAlreadyExists


class SqlManager(BaseManagerInterface):
    db_type = "sql"

    def _get_queryable_class(self):
        klass = self.klass
        if not isinstance(self.klass, DeclarativeMeta):
            klass = self.klass.__class__
        return klass

    def _is_transient(self) -> bool:
        return inspect(self.klass).transient

    def save(self):
        try:
            with self.db.Session() as sess:
                sess.add(self.klass)
        except sqlalchemy.exc.IntegrityError as exc:
            raise ObjectAlreadyExists(exc.args[0]) from None

    def delete(self) -> None:
        with self.db.Session() as sess:
            sess.delete(self.klass)

    def get(self, identifier):
        klass = self._get_queryable_class()

        with self.db.Session() as sess:
            obj = sess.query(klass).get(identifier)
            if not obj:
                raise ObjectNotFound(
                    f"Object of type '{klass.__name__}' "
                    f"with primary key '{identifier}', could not be found."
                )
            return obj

    def filter(self, **kwargs):
        klass = self._get_queryable_class()

        with self.db.Session() as sess:
            return sess.query(klass).filter_by(**kwargs).all()

    def all(self):
        klass = self._get_queryable_class()

        with self.db.Session() as sess:
            return sess.query(klass).all()
