# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-04-24 18:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20170418_0846'),
    ]

    operations = [
        migrations.AddField(
            model_name='invites',
            name='used_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
