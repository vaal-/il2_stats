# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0006_score_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='object',
            name='is_playable',
            field=models.BooleanField(default=False),
        ),
    ]
