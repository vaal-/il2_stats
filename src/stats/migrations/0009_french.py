# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0008_auto_20151119_2230'),
    ]

    operations = [
        migrations.AddField(
            model_name='object',
            name='name_fr',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='tour',
            name='title_fr',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
