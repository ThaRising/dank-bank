from .base import BaseManagerInterface


class SqlManager(BaseManagerInterface):
    def _get_storage(self):
        from ..storage import Storage
        return Storage()

    def save(self) -> None:
        with self.db.Session() as sess:
            sess.add(self.model_instance)

    def update(self, data: dict) -> None:
        with self.db.Session():
            for k, v in data.items():
                setattr(self.model_instance, k, v)

    def delete(self, **kwargs) -> None:
        with self.db.Session() as sess:
            sess.delete(self.model_instance)

    def read(model_class: DeclarativeMeta,
             *args, **kwargs) -> Union[list, DeclarativeMeta]:
        from . import get_storage
        storage = get_storage()

        # if the user has not provided any kwargs like 'pk=3'
        # then we can assume they want all rows of the given table
        if not kwargs and not args:
            with storage.Session() as sess:
                return sess.query(model_class).all()

        # if they did provide kwargs we can filter
        if kwargs:
            with storage.Session() as sess:
                return sess.query(model_class).filter_by(**kwargs).all()

        elif args:
            with storage.Session() as sess:
                return sess.query(model_class).get(args[0])
