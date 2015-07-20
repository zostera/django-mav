from __future__ import unicode_literals

from django.db import models

from .models import BaseValue, generate_value_class


def mav_attrs(model_class, *args, **kwargs):
    return model_class, generate_value_class(model_class, *args, **kwargs)