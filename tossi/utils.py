# -*- coding: utf-8 -*-
"""
   tossi.utils
   ~~~~~~~~~~~

   Utilities for internal use.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import functools


__all__ = ['cached_property', 'CacheMeta']


def cached_property(f):
    """Similar to `@property` but it calls the function just once and caches
    the result.  The object has to can have ``__cache__`` attribute.

    If you define `__slots__` for optimization, the metaclass should bea
    :class:`CacheMeta`.

    """
    @property
    @functools.wraps(f)
    def wrapped(self, name=f.__name__):
        try:
            cache = self.__cache__
        except AttributeError:
            self.__cache__ = cache = {}
        try:
            return cache[name]
        except KeyError:
            cache[name] = rv = f(self)
            return rv
    return wrapped


class CacheMeta(type):

    def __new__(meta, name, bases, attrs):
        if '__slots__' in attrs:
            attrs['__slots__'] += ('__cache__',)
        return super(CacheMeta, meta).__new__(meta, name, bases, attrs)
