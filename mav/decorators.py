from __future__ import unicode_literals, absolute_import

from .models import add_mav_to


def _mav(cls, *args, **kwargs):
    """
    Add mav to a model class and return that model class
    :param cls: The model class that needs mav
    :return: The model class
    """
    add_mav_to(cls, *args, **kwargs)
    return cls


def mav(cls=None, **kwargs):
    """
    Smart decorator class to add mav to a model class, and can optionally take arguments
    :param cls: The model class that needs mav
    :return: Class (when called with cls argument) or wrapper class (when called without cls argument)
    """
    if cls:
        return _mav(cls)
    else:
        def wrapper(cls):
            return _mav(cls, **kwargs)
        return wrapper
