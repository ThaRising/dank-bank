from sqlalchemy.ext.hybrid import hybrid_property


class ManagerMixin:
    @property
    def objects(self):
        return None
