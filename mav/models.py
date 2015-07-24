from __future__ import unicode_literals

import datetime

from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from . import attrs


class Unit(models.Model):
    """
    A unit for a given attribute
    """
    name = models.CharField(_('name'), max_length=100, db_index=True)
    symbol = models.CharField(_('symbol'), max_length=10)

    def __unicode__(self):
        return self.name


class Attribute(models.Model):
    """
    An attribute for a model (the 'A' in EAV/OAV)
    """
    TYPE_TEXT = 1
    TYPE_BOOLEAN = 2
    TYPE_INTEGER = 3
    TYPE_DECIMAL = 4
    TYPE_DATE = 5
    TYPE_TIME = 6

    BOOLEAN_TRUE_TEXTS = ('TRUE', 'YES', 'T', 'Y', '1',)
    BOOLEAN_FALSE_TEXTS = ('FALSE', 'NO', 'F', 'N', '0',)
    BOOLEAN_NULL_TEXTS = ('NULL', '',)

    CHOICES_FOR_TYPE = (
        (TYPE_TEXT, _('text')),
        (TYPE_BOOLEAN, _('boolean')),
        (TYPE_INTEGER, _('integer')),
        (TYPE_DECIMAL, _('decimal')),
        (TYPE_DATE, _('date')),
        (TYPE_TIME, _('time')),
    )

    slug = models.SlugField(verbose_name=_('slug'), unique=True)
    name = models.CharField(_('name'), max_length=100, db_index=True)
    type = models.PositiveSmallIntegerField(_('type'), choices=CHOICES_FOR_TYPE)
    unit = models.ForeignKey('Unit', verbose_name=_('unit'), null=True, blank=True)

    def get_name_display(self):
        if self.name:
            return self.name
        return self.slug

    def get_label(self):
        label_parts = [self.get_name_display(), ]
        if self.unit:
            label_parts.append('({symbol})'.format(symbol=self.unit.symbol))
        return ' '.join(label_parts)

    def get_choices(self):
        if self.type == self.TYPE_BOOLEAN:
            return (
                ('', _('unknown')),
                ('TRUE', _('yes')),
                ('FALSE', _('no')),
            )
        return [(choice.pk, choice.get_value_display()) for choice in self.choice_set.order_by('sort_order', 'name')]

    def text_to_value(self, text):
        if self.type == self.TYPE_TEXT:
            return text
        t = text.upper().strip()
        if self.type == self.TYPE_INTEGER:
            return int(t)
        if self.type == self.TYPE_DECIMAL:
            return float(t)
        if self.type == self.TYPE_BOOLEAN:
            if t in self.BOOLEAN_TRUE_TEXTS:
                return True
            if t in self.BOOLEAN_FALSE_TEXTS:
                return False
            if t in self.BOOLEAN_NULL_TEXTS:
                return None
        if self.type == self.TYPE_DATE:
            parts = text.split('-')
            return datetime.date(
                int(parts[0].strip()),
                int(parts[1].strip()),
                int(parts[2].strip()),
            )
        if self.type == self.TYPE_TIME:
            parts = text.split(':')
            hours = int(parts[0].strip())
            try:
                minutes = int(parts[1].strip())
            except IndexError:
                minutes = 0
            try:
                seconds = int(parts[2].strip())
            except IndexError:
                seconds = 0
            return datetime.time(hours, minutes, seconds)
        # We cannot parse this
        raise ValueError('Cannot convert text "{text}" to value of type {type}.'.format(
            text=text,
            type=self.get_type_display()
        ))

    def __unicode__(self):
        return self.get_name_display()


class Choice(models.Model):
    attribute = models.ForeignKey(Attribute)
    value = models.CharField(_('value'), max_length=100, blank=True)
    name = models.CharField(_('name'), max_length=100, blank=True)
    description = models.TextField(_('description'), blank=True)
    sort_order = models.IntegerField(_('sort order'), default=0)

    def get_value_display(self):
        if self.name:
            return self.name
        return self.value

    def __unicode__(self):
        return '{attribute}.{name}'.format(attribute=self.attribute.name, name=self.get_value_display())

    class Meta:
        ordering = ['attribute_id', 'sort_order', 'value', 'pk', ]


class AbstractModelAttribute(models.Model):
    attribute = models.ForeignKey(Attribute)
    value = models.CharField(_('value'), max_length=100, blank=True)

    def get_value_display(self):
        value = '{}'.format(self.value)
        if self.attribute.choice_set.exists():
            choice_values = []
            for choice in value.split(','):
                try:
                    choice_id = int(choice)
                except ValueError:
                    choice_values.append('!!!error!!!')
                else:
                    try:
                        choice = Choice.objects.get(pk=choice_id)
                    except Choice.DoesNotExist:
                        choice_values.append('!!!not_found!!!')
                    else:
                        choice_values.append(choice.get_value_display())
            value = ', '.join(choice_values)
        return value

    def __unicode__(self):
        return '{attribute} = {value}'.format(
            attribute=self.attribute,
            value=self.get_value_display(),
        )

    class Meta:
        abstract = True


def create_model_attribute_class(model, class_name=None, related_name=None, meta=None):
    """
    Generate a value class (derived from AbstractModelAttribute) for a given model class
    :param model: The model to create a AbstractModelAttribute class for
    :param class_name: The name of the AbstractModelAttribute class to generate
    :param related_name: The related name
    :return: A model derives from AbstractModelAttribute with an object pointing to model_class
    """

    if model._meta.abstract:
        # This can't be done, because `object = ForeignKey(model_class)` would fail.
        raise TypeError("Can't create mav for abstract class {0}".format(model.__name__))

    # Define inner Meta class
    if not meta:
        meta = {}

    # Force only one value for each model, attribute set
    meta['unique_together'] = list(meta.get('unique_together', [])) + [('attribute', 'object')]

    # Use the same tablespace as the model
    meta['db_tablespace'] = model._meta.db_tablespace

    # Use same setting for managed as model
    meta['managed'] = model._meta.managed

    # Set the default db table
    meta.setdefault('db_table', '{0}_attr'.format(model._meta.db_table))

    # The name of the class to generate
    if class_name is None:
        value_class_name = '{name}Attr'.format(name=model.__name__)
    else:
        value_class_name = class_name

    # The related name to set
    if related_name is None:
        model_class_related_name = 'attrs'
    else:
        model_class_related_name = related_name

    # Make a type for our class
    value_class = type(
        str(value_class_name),
        (AbstractModelAttribute,),
        dict(
            # Set to same module as model_class
            __module__=model.__module__,
            # Add a foreign key to model_class
            object=models.ForeignKey(
                model,
                related_name=model_class_related_name
            ),
            # Add Meta class
            Meta=type(
                str('Meta'),
                (object,),
                meta
            ),
        ))

    return value_class


def add_mav_to(model, class_name=None, related_name=None, meta=None):
    """
    Patch model class to have mav attributes
    :param model: The model class to patch
    :param class_name: The name of the class to generate
    :param related_name: The related_name to set in the model
    :return: The generated class
    """

    # Generate the class
    mav_class = create_model_attribute_class(
        model=model,
        class_name=class_name,
        related_name=related_name,
        meta=meta,
    )

    # Add it to .attrs
    setattr(attrs, mav_class.__name__, mav_class)

    # Link it to the model
    model._mav_class = mav_class

    # Return the generated class
    return mav_class
