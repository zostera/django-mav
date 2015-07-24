==========
django-mav
==========

An implementation of model-attribute-value for Django, without using generic relations.


Installation
------------

1. Install using pip (soon - use GitHub for now):

   ``pip install django-mav``

   Alternatively, you can install download or clone this repo and call ``pip install -e .``.

2. Add to INSTALLED_APPS in your ``settings.py``:

   ``'mav',``

3. In your models, decorate models that need to store model-attribute-values with ``@mav``.


Example code (foo/models.py)
----------------------------

.. code:: Django

    from django.db import models
    
    from mav.decorators import mav
    
    @mav
    class Foo(models.Model):
        name = models.CharField(max_length=100)
    
    # The @mav decorator will generate a FooAttr class in mav.attrs:
    
    class FooAttr(AbstractModelAttribute):
        # Inherited from AbstractModelAttribute
        attribute = models.ForeignKey(Attribute)
        value = models.TextField(...)
        # Generated
        object = models.ForeignKey(Foo, related_name='attrs')


Documentation
-------------

TODO


Requirements
------------

- Python 2.6, 2.7, 3.2 or 3.3
- Django >= 1.4

Contributions and pull requests for other Django and Python versions are welcome.


Bugs and requests
-----------------

If you have found a bug or if you have a request for additional functionality, please use the issue tracker on GitHub.

https://github.com/zostera/django-mav/issues


License
-------

You can use this under the MIT License. See `LICENSE <LICENSE>`_ file for details.


Author
------

Developed and maintained by `Zostera <https://zostera.nl/>`_.

Original author & Development lead: `Dylan Verheul <https://github.com/dyve>`_.

Thanks to everybody that has contributed pull requests, ideas, issues, comments and kind words.

Please see AUTHORS.rst for a list of contributors.
