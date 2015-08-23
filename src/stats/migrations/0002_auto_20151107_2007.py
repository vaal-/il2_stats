# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='object',
            name='name_de',
            field=models.CharField(blank=True, null=True, max_length=64),
        ),
        migrations.AddField(
            model_name='tour',
            name='title_de',
            field=models.CharField(blank=True, null=True, max_length=32),
        ),
    ]
