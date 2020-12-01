from inspect import isclass

from ..utils import hybrid_property


class ManagerMixin:
    @hybrid_property
    def objects(klass):  # noqa attr self
        # we need to take the Manager from the class exclusively,
        # otherwise it will inject 'self' as the first positional parameter,
        # which is the default behaviour of class instances
        if not isclass(klass):
            # if it is an instance, get its class object to
            # get the 'manager' attribute from
            cls = klass.__class__
        else:
            cls = klass
        return cls.manager(klass)  # noqa unresolved
