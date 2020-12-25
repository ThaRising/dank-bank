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

    def update(self, data: dict):
        with self.db.Session():
            for k, v in data.items():
                setattr(self.klass, k, v)
        return self.klass

    def delete(self) -> None:
        with self.db.Session() as sess:
            sess.delete(self.klass)

    def _read(self, *args, **kwargs):
        # if the user has not provided any kwargs like 'pk=3'
        # then we can assume they want all rows of the given table
        klass = self._get_queryable_class()

        if not kwargs and not args:
            with self.db.Session() as sess:
                return sess.query(klass).all()

        # if they did provide kwargs we can filter
        if kwargs:
            with self.db.Session() as sess:
                return sess.query(klass).filter_by(**kwargs).all()

        elif args:
            if len(args) > 1:
                raise ValueError(
                    "A maximum of one positional argument may be provided."
                )
            with self.db.Session() as sess:
                pk = args[0]
                obj = sess.query(klass).get(pk)
                if not obj:
                    raise ObjectNotFound(
                        f"Object of type '{klass.__name__}' with primary key '{pk}', "
                        f"could not be found."
                    )
                return obj
