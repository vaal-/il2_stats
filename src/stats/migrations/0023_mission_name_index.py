# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-24 19:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0022_online'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mission',
            name='name',
            field=models.CharField(blank=True, db_index=True, max_length=256),
        ),
    ]
