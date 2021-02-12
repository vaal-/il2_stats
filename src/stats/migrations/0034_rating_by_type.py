# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0033_award_order_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='score_bomber',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='score_attacker',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='score_fighter',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='rating_bomber',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='rating_attacker',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='rating_fighter',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]