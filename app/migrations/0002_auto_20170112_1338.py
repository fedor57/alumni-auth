# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-12 13:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='invites',
            name='disabled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='invites',
            name='status',
            field=models.SmallIntegerField(choices=[(1, b'OK'), (2, b'DISABLED')], default=1),
        ),
    ]
