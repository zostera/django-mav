from __future__ import unicode_literals

from django import forms
from django.contrib import admin

from .models import Attribute, Choice, Unit


try:
    from modeltranslation.admin import TranslationAdmin as AdminClass
except ImportError:
    AdminClass = admin.ModelAdmin


admin.site.register(Attribute, AdminClass)
admin.site.register(Choice, AdminClass)
admin.site.register(Unit, AdminClass)
