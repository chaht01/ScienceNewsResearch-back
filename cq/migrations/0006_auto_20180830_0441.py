# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-08-30 04:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cq', '0005_auto_20180830_0406'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='codesecond',
            name='first_code',
        ),
        migrations.AddField(
            model_name='codesecond',
            name='code_first',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='code_seconds', to='cq.Codefirst'),
        ),
    ]
