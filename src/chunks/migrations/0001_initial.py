# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chunk',
            fields=[
                ('key', models.CharField(max_length=32, verbose_name='key', primary_key=True, help_text='A unique name for this chunk of content', serialize=False)),
                ('title', models.CharField(max_length=255, verbose_name='title', blank=True)),
                ('title_en', models.CharField(max_length=255, verbose_name='title', null=True, blank=True)),
                ('title_ru', models.CharField(max_length=255, verbose_name='title', null=True, blank=True)),
                ('content', models.TextField(verbose_name='content', blank=True)),
                ('content_en', models.TextField(verbose_name='content', null=True, blank=True)),
                ('content_ru', models.TextField(verbose_name='content', null=True, blank=True)),
            ],
            options={
                'db_table': 'chunks',
            },
        ),
    ]
