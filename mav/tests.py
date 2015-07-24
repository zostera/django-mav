# coding: utf-8
from __future__ import unicode_literals

import datetime
from django.db import models

from django.test import TestCase

from model_mommy import mommy
from mav.decorators import mav

from .models import Attribute

@mav
class Foo(models.Model):
    name = models.CharField(max_length=100)


class ValueTestCase(TestCase):
    def test_unit_symbol(self):
        """
        Test display of strange symbols in units
        """
        unit_celsius = mommy.make('mav.Unit', name='degrees Celsius', symbol='° C')
        self.assertEqual('° C', unit_celsius.symbol)

    def test_attribute_type_text(self):
        """
        Test parsing of text to text value
        """
        attribute = mommy.make(Attribute, type=Attribute.TYPE_TEXT)
        self.assertEqual('text value', attribute.text_to_value('text value'))

    def test_attribute_type_integer(self):
        """
        Test parsing of text to integer value
        """
        attribute = mommy.make(Attribute, type=Attribute.TYPE_INTEGER)
        self.assertEqual(189, attribute.text_to_value('189'))
        with self.assertRaises(ValueError):
            attribute.text_to_value('189.1')
        with self.assertRaises(ValueError):
            attribute.text_to_value('this.is.not.an.integer')

    def test_attribute_type_decimal(self):
        """
        Test parsing of text to decimal value
        """
        attribute = mommy.make(Attribute, type=Attribute.TYPE_DECIMAL)
        self.assertEqual(189, attribute.text_to_value('189'))
        self.assertEqual(189.1, attribute.text_to_value('189.1'))
        with self.assertRaises(ValueError):
            attribute.text_to_value('this.is.not.a.decimal')

    def test_attribute_type_boolean(self):
        """
        Test parsing of text to boolean value
        """
        attribute = mommy.make(Attribute, type=Attribute.TYPE_BOOLEAN)
        for text in Attribute.BOOLEAN_TRUE_TEXTS:
            self.assertEqual(True, attribute.text_to_value(text))
        for text in Attribute.BOOLEAN_FALSE_TEXTS:
            self.assertEqual(False, attribute.text_to_value(text))
        for text in Attribute.BOOLEAN_NULL_TEXTS:
            self.assertEqual(None, attribute.text_to_value(text))
        with self.assertRaises(ValueError):
            attribute.text_to_value('this.is.not.a.boolean')

    def test_attribute_type_date(self):
        """
        Test parsing of text to date value
        """
        date = datetime.date(2000, 2, 29)
        date_texts = ['2000-02-29', '2000-2-29', ]
        attribute = mommy.make(Attribute, type=Attribute.TYPE_DATE)
        for text in date_texts:
            self.assertEqual(date, attribute.text_to_value(text))
        with self.assertRaises(ValueError):
            attribute.text_to_value('this.is.not.a.date')

    def test_attribute_type_time(self):
        """
        Test parsing of text to time value
        """
        time = datetime.time(23, 1, 15)
        time_texts = ['23:01:15', '23:1:15', ]
        attribute = mommy.make(Attribute, type=Attribute.TYPE_TIME)
        for text in time_texts:
            self.assertEqual(time, attribute.text_to_value(text))
        with self.assertRaises(ValueError):
            attribute.text_to_value('this.is.not.a.time')

    def test_class_with_attrs(self):
        """
        Test to see if class with attrs behaves
        """
        bar = Attribute(type=Attribute.TYPE_TEXT, slug='bar')
        bar.save()
        foo = Foo(name='foo')
        foo.save()
        self.assertEqual(bar.slug, 'bar')
        mav_class = Foo._mav_class
        from mav.attrs import FooAttr
        self.assertEqual(FooAttr, mav_class)
        attr = mav_class(attribute=bar, object=foo, value='foobar')
        attr.save()
        self.assertEqual(attr.value, 'foobar')
        self.assertEqual(attr.object, foo)
        self.assertEqual(attr.attribute, bar)
