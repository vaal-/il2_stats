# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0007_object_is_playable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='object',
            name='cls',
            field=models.CharField(max_length=24, choices=[('aaa_heavy', 'aaa_heavy'), ('aaa_light', 'aaa_light'), ('aaa_mg', 'aaa_mg'), ('aircraft_gunner', 'aircraft_gunner'), ('aircraft_heavy', 'aircraft_heavy'), ('aircraft_light', 'aircraft_light'), ('aircraft_medium', 'aircraft_medium'), ('aircraft_pilot', 'aircraft_pilot'), ('aircraft_static', 'aircraft_static'), ('aircraft_transport', 'aircraft_transport'), ('aircraft_turret', 'aircraft_turret'), ('armoured_vehicle', 'armoured_vehicle'), ('artillery_field', 'artillery_field'), ('artillery_howitzer', 'artillery_howitzer'), ('artillery_rocket', 'artillery_rocket'), ('block', 'block'), ('bomb', 'bomb'), ('bullet', 'bullet'), ('car', 'car'), ('driver', 'driver'), ('explosion', 'explosion'), ('locomotive', 'locomotive'), ('machine_gunner', 'machine_gunner'), ('parachute', 'parachute'), ('rocket', 'rocket'), ('searchlight', 'searchlight'), ('ship', 'ship'), ('shell', 'shell'), ('tank_heavy', 'tank_heavy'), ('tank_light', 'tank_light'), ('tank_medium', 'tank_medium'), ('tank_driver', 'tank_driver'), ('tank_turret', 'tank_turret'), ('trash', 'trash'), ('truck', 'truck'), ('vehicle_crew', 'vehicle_crew'), ('vehicle_static', 'vehicle_static'), ('vehicle_turret', 'vehicle_turret'), ('wagon', 'wagon')], blank=True),
        ),
        migrations.AlterField(
            model_name='object',
            name='is_playable',
            field=models.BooleanField(editable=False, default=False),
        ),
        migrations.AlterField(
            model_name='player',
            name='type',
            field=models.CharField(max_length=8, choices=[('pilot', 'pilot'), ('gunner', 'gunner'), ('tankman', 'tankman')], db_index=True, default='pilot'),
        ),
    ]
