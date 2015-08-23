# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0004_sortie_score_dict'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sortie',
            name='score_wo_bonus',
        ),
    ]
