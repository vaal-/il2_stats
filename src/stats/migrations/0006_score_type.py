# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0005_remove_sortie_score_wo_bonus'),
    ]

    operations = [
        migrations.AddField(
            model_name='score',
            name='type',
            field=models.CharField(editable=False, choices=[('int', 'integer'), ('pct', 'percent')], max_length=3, default='int'),
        ),
        migrations.AlterField(
            model_name='logentry',
            name='type',
            field=models.CharField(choices=[('respawn', 'respawn'), ('end', 'end'), ('takeoff', 'takeoff'), ('landed', 'landed'), ('ditched', 'ditched'), ('crashed', 'crashed'), ('bailout', 'bailout'), ('damaged', 'damaged'), ('wounded', 'wounded'), ('killed', 'killed'), ('destroyed', 'destroyed'), ('shotdown', 'shotdown')], db_index=True, max_length=16),
        ),
    ]
