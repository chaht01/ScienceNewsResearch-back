# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-08-30 04:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cq', '0004_auto_20180830_0312'),
    ]

    operations = [
        migrations.RenameField(
            model_name='question',
            old_name='copied_from',
            new_name='copied_to',
        ),
    ]