# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-09-05 13:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cq', '0009_auto_20180905_1347'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='judgement',
            name='similarity',
        ),
        migrations.DeleteModel(
            name='Similarity',
        ),
    ]
