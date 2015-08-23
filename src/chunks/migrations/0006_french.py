# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chunks', '0005_server_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='chunk',
            name='content_fr',
            field=models.TextField(null=True, blank=True, verbose_name='content'),
        ),
        migrations.AddField(
            model_name='chunk',
            name='title_fr',
            field=models.CharField(null=True, blank=True, verbose_name='title', max_length=255),
        ),
    ]
