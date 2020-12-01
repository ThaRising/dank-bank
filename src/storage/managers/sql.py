from typing import Union

from sqlalchemy.ext.declarative import DeclarativeMeta

from .base import BaseManagerInterface


class SqlManager(BaseManagerInterface):
    def save(self) -> None:
        with self.db.Session() as sess:
            sess.add(self.klass)

    def update(self, data: dict) -> None:
        with self.db.Session():
            for k, v in data.items():
                setattr(self.klass, k, v)

    def delete(self, **kwargs) -> None:
        with self.db.Session() as sess:
            sess.delete(self.klass)

    def read(self, *args, **kwargs) -> Union[list, DeclarativeMeta]:
        # if the user has not provided any kwargs like 'pk=3'
        # then we can assume they want all rows of the given table
        if not kwargs and not args:
            with self.db.Session() as sess:
                return sess.query(self.klass.__class__).all()

        # if they did provide kwargs we can filter
        if kwargs:
            with self.db.Session() as sess:
                return sess.query(self.klass).filter_by(**kwargs).all()

        elif args:
            with self.db.Session() as sess:
                return sess.query(self.klass).get(args[0])
