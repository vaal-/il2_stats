# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chunks', '0002_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='chunk',
            name='content_de',
            field=models.TextField(verbose_name='content', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='chunk',
            name='title_de',
            field=models.CharField(max_length=255, verbose_name='title', null=True, blank=True),
        ),
    ]
