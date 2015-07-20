from __future__ import unicode_literals
from collections import OrderedDict

from django import forms
from django.template.defaultfilters import capfirst

from .models import Attribute, Choice, AbstractModelAttribute


FIELD_PREFIX = '__mav__'


class RelaxedFloatField(forms.FloatField):
    """
    Allow both comma and point as decimal separator, unless you use both
    """

    def clean(self, value):
        value = unicode(value)
        if ',' in value and not '.' in value:
            value = value.replace(',', '.')
        return super(RelaxedFloatField, self).clean(value)


def generate_attribute_field(attribute, value=''):
    """
    Generate a attribute field
    """
    choices = attribute.get_choices()
    if choices:
        required = True
        for choice in choices:
            if choice[0] == '':
                required = False
        field = forms.ChoiceField(choices=choices, required=required, initial=value)
    elif attribute.type == Attribute.TYPE_INTEGER:
        field = forms.IntegerField(required=False, initial=value)
    elif attribute.type == Attribute.TYPE_DECIMAL:
        field = RelaxedFloatField(required=False, initial=value)
    elif attribute.type == Attribute.TYPE_DATE:
        field = forms.DateField(required=False, initial=value)
        field.widget.attrs['data-datepicker'] = True
    else:
        field = forms.CharField(required=False, initial=value)
    field.label = capfirst(attribute.get_label())
    return field


def add_attribute_field_to_form(form, attribute, value=''):
    """
    Add field for attribute to form
    """
    field_name = '{prefix}{id}'.format(prefix=FIELD_PREFIX, id=attribute.id)
    field = generate_attribute_field(attribute, value)
    form.fields[field_name] = field
    return form


def add_attribute_fields_to_form(form, attributes, attrs):
    """
    Add fields for attributes to form
    form = form to modify
    attributes = attributes to add (Attribute)
    attrs = existing attributes (AbstractModelAttribute)
    """
    existing = OrderedDict()
    # Find existing attributes
    if attrs:
        for attr in attrs:
            attribute = attr.attribute
            existing[attribute.id] = attr.value
    # Add fields for the attributes
    if attributes:
        for attribute in attributes:
            value = existing.pop(attribute.id, '')
            add_attribute_field_to_form(form, attribute, value)
    # See if we have attributes for unlisted attributes and add those too
    for attribute_id in existing:
        value = existing[attribute_id]
        attribute = Attribute.objects.get(pk=attribute_id)
        add_attribute_field_to_form(form, attribute, value)
    # Return the form
    return form


def save_attribute_fields(form):
    """
    Save the attribute fields of a form to attributes
    """
    instance = form.instance
    attributes = {}
    pos = len(FIELD_PREFIX)
    for k in form.cleaned_data:
        if k[0:pos] == FIELD_PREFIX:
            attribute_id = k[pos:]
            attributes[attribute_id] = form.cleaned_data[k]
    if attributes:
        # Process all attributes
        for attribute_id in attributes:
            # We need content_type, see above
            value, created = instance.attrs.get_or_create(
                attribute_id=attribute_id,
                object=instance,
            )
            # Set the value (don't allow None)
            value.value = attributes[attribute_id]
            if value.value is None:
                value.value = ''
            # And save the value
            value.save()


class AttrsModelFormMixin(object):
    """
    Mixin to handle attributes in a ModelForm
    """

    def __init__(self, *args, **kwargs):
        # Create the form
        super(AttrsModelFormMixin, self).__init__(*args, **kwargs)
        # Modify the form
        add_attribute_fields_to_form(self, self.get_attributes(), self.get_attrs())

    def get_attributes(self):
        """
        Get all attributes that should be on the form
        """
        try:
            return self.instance.get_attributes()
        except AttributeError:
            return None

    def get_attrs(self):
        """
        Get existing attributes with values
        """
        try:
            return self.instance.attrs.all()
        except AttributeError:
            return None

    def save(self, commit=True):
        instance = super(AttrsModelFormMixin, self).save(commit=commit)
        if commit:
            save_attribute_fields(self)
        else:
            # Modify the save_m2m of the model
            super_save_m2m = self.save_m2m
            def save_m2m():
                super_save_m2m()
                save_attribute_fields(self)
            self.save_m2m = save_m2m
        return instance


class ModelFormWithAttrs(AttrsModelFormMixin, forms.ModelForm):
    """
    A ModelForm that also handles attributes and attributes
    """
    pass