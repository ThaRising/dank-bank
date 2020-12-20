class ObjectNotFound(Exception):
    pass


class ObjectAlreadyExists(Exception):
    pass


__all__ = ["ObjectNotFound", "ObjectAlreadyExists"]