"""
Classes that uses for lazy loading of objects.

Check `BaseString.lazy_give` and `conf.lazy_prefix`
"""

import operator


class LazyObject:
    def __init__(self, factory):
        # Assign using __dict__ to avoid the setattr method.
        self.__dict__["_factory"] = factory

    def new_method_proxy(func):
        """
        Util function to help us route functions
        to the nested object.
        """

        def inner(self, *args):
            return func(self._factory(), *args)

        return inner

    def __call__(self, *args, **kwargs):
        return self._factory()(*args, **kwargs)

    __getattr__ = new_method_proxy(getattr)
    __bytes__ = new_method_proxy(bytes)
    __str__ = new_method_proxy(str)
    __bool__ = new_method_proxy(bool)
    __dir__ = new_method_proxy(dir)
    __hash__ = new_method_proxy(hash)
    __class__ = property(new_method_proxy(operator.attrgetter("__class__")))
    __eq__ = new_method_proxy(operator.eq)
    __lt__ = new_method_proxy(operator.lt)
    __le__ = new_method_proxy(operator.le)
    __gt__ = new_method_proxy(operator.gt)
    __ge__ = new_method_proxy(operator.ge)
    __ne__ = new_method_proxy(operator.ne)
    __mod__ = new_method_proxy(operator.mod)
    __hash__ = new_method_proxy(hash)
    __getitem__ = new_method_proxy(operator.getitem)
    __iter__ = new_method_proxy(iter)
    __len__ = new_method_proxy(len)
    __contains__ = new_method_proxy(operator.contains)
    __mul__ = new_method_proxy(operator.mul)
    __rmul__ = new_method_proxy(operator.mul)
    __not__ = new_method_proxy(operator.not_)
    __bool__ = new_method_proxy(bool)
    __len__ = new_method_proxy(len)
    __abs__ = new_method_proxy(operator.abs)
    __add__ = new_method_proxy(operator.add)
    __radd__ = new_method_proxy(operator.add)
    __and__ = new_method_proxy(operator.and_)
    __floordiv__ = new_method_proxy(operator.floordiv)
    __index__ = new_method_proxy(operator.index)
    __inv__ = new_method_proxy(operator.inv)
    __invert__ = new_method_proxy(operator.invert)
    __lshift__ = new_method_proxy(operator.lshift)
    __mod__ = new_method_proxy(operator.mod)
    __matmul__ = new_method_proxy(operator.matmul)
    __neg__ = new_method_proxy(operator.neg)
    __or__ = new_method_proxy(operator.or_)
    __pos__ = new_method_proxy(operator.pos)
    __pow__ = new_method_proxy(operator.pow)
    __rshift__ = new_method_proxy(operator.rshift)
    __sub__ = new_method_proxy(operator.sub)
    __truediv__ = new_method_proxy(operator.truediv)
    __xor__ = new_method_proxy(operator.xor)
    __concat__ = new_method_proxy(operator.concat)
    __contains__ = new_method_proxy(operator.contains)
    __delitem__ = new_method_proxy(operator.delitem)
    __getitem__ = new_method_proxy(operator.getitem)
    __setitem__ = new_method_proxy(operator.setitem)
    __call__ = new_method_proxy(operator.call)
    __iadd__ = new_method_proxy(operator.iadd)
    __iand__ = new_method_proxy(operator.iand)
    __iconcat__ = new_method_proxy(operator.iconcat)
    __ifloordiv__ = new_method_proxy(operator.ifloordiv)
    __ilshift__ = new_method_proxy(operator.ilshift)
    __imod__ = new_method_proxy(operator.imod)
    __imul__ = new_method_proxy(operator.imul)
    __imatmul__ = new_method_proxy(operator.imatmul)
    __ior__ = new_method_proxy(operator.ior)
    __ipow__ = new_method_proxy(operator.ipow)
    __irshift__ = new_method_proxy(operator.irshift)
    __isub__ = new_method_proxy(operator.isub)
    __itruediv__ = new_method_proxy(operator.itruediv)
    __ixor__ = new_method_proxy(operator.ixor)
    __next__ = new_method_proxy(next)
    __reversed__ = new_method_proxy(reversed)
    __round__ = new_method_proxy(round)
