# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0002_auto_20151107_2007'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='fairplay_time',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='sortie',
            name='fairplay',
            field=models.IntegerField(default=100),
        ),
    ]
