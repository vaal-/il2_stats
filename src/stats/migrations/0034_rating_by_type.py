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
            name='score_heavy',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='score_medium',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='score_light',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='rating_heavy',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='rating_medium',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='rating_light',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='relive_heavy',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='relive_medium',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='relive_light',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='flight_time_heavy',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='flight_time_medium',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='player',
            name='flight_time_light',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='PlayerMission',
            name='score_heavy',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='PlayerMission',
            name='score_medium',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='PlayerMission',
            name='score_light',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]