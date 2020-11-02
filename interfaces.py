from abc import ABC, abstractmethod
from typing import Any, Union


class CrudInterface(ABC):
    model: Any
    db: Any

    @abstractmethod
    def create(self, *args, **kwargs):
        pass

    def read(self, **kwargs) -> Union[list, "model"]:
        with self.db.Session() as sess:
            if kwargs:
                return sess.query(self.model).get(**kwargs)
            else:
                sess.query(self.model).all()

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    def delete(self, **kwargs) -> None:
        with self.db.Session() as sess:
            elem = sess.query(self.model).get(**kwargs)
            sess.delete(elem)
