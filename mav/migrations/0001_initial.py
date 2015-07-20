# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(unique=True, verbose_name='slug')),
                ('name', models.CharField(max_length=100, verbose_name='name', db_index=True)),
                ('type', models.PositiveSmallIntegerField(verbose_name='type', choices=[(1, 'text'), (2, 'boolean'), (3, 'integer'), (4, 'decimal'), (5, 'date'), (6, 'time')])),
            ],
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=100, verbose_name='value', blank=True)),
                ('name', models.CharField(max_length=100, verbose_name='name', blank=True)),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('sort_order', models.IntegerField(default=0, verbose_name='sort order')),
                ('attribute', models.ForeignKey(to='mav.Attribute')),
            ],
            options={
                'ordering': ['attribute_id', 'sort_order', 'value', 'pk'],
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name', db_index=True)),
                ('symbol', models.CharField(max_length=10, verbose_name='symbol')),
            ],
        ),
        migrations.AddField(
            model_name='attribute',
            name='unit',
            field=models.ForeignKey(verbose_name='unit', blank=True, to='mav.Unit', null=True),
        ),
    ]
