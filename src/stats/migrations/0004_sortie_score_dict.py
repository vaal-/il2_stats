# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields.jsonb


def update_score_dict(apps, schema_editor):
    Sortie = apps.get_model('stats', 'Sortie')
    for s in Sortie.objects.all():
        s.score_dict = {
            'basic': s.score_wo_bonus,
            'bonus': s.score - s.score_wo_bonus,
        }
        s.save()


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0003_fairplay'),
    ]

    operations = [
        migrations.AddField(
            model_name='sortie',
            name='score_dict',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
        migrations.RunPython(update_score_dict),
    ]
