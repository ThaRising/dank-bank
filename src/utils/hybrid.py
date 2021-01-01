class hybrid_property:
    """ Mostly ripped from the SQLAlchemy sourcecode (MIT-License) """

    def __init__(self, fget=None, fset=None, fdel=None, fcget=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.fcget = fcget

    def __get__(self, instance, owner):
        if instance is None:
            if self.fcget is None and self.fget is None:
                raise AttributeError("unreadable attribute")
            return (self.fcget or self.fget)(owner)
        else:
            if self.fget is None:
                raise AttributeError("unreadable attribute")
            return self.fget(instance)

    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(instance, value)

    def __delete__(self, instance):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(instance)

    def getter(self, fget):
        """
        Returns a new `hybrid_property` instance with `fget` set to the given
        function.
        """
        return self._copy(fget=fget)

    def setter(self, fset):
        """
        Returns a new `hybrid_property` instance with `fset` set to the given
        function.
        """
        return self._copy(fset=fset)

    def deleter(self, fdel):
        """
        Returns a new `hybrid_property` instance with `fdel` set to the given
        function.
        """
        return self._copy(fdel=fdel)

    def classgetter(self, fcget):
        """
        Returns a new `hybrid_property` instance with `fcget` set to the given
        function.
        """
        return self._copy(fcget=fcget)

    def _copy(self, fget=None, fset=None, fdel=None, fcget=None):
        return self.__class__(
            fget=self.fget if fget is None else fget,
            fset=self.fset if fset is None else fset,
            fdel=self.fdel if fdel is None else fdel,
            fcget=self.fcget if fcget is None else fcget,
        )
