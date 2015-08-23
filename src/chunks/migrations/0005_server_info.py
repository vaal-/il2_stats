# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

info_en = '''
<h3>Description</h3>
<p>
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer venenatis arcu orci,
    vel feugiat nulla sagittis in. Duis varius ipsum in urna condimentum, sed vestibulum metus tincidunt.
    Proin nisl metus, mattis et ullamcorper facilisis, commodo in dolor. Quisque turpis lacus,
    gravida et dictum in, cursus id tellus. Cras vitae nunc eu tellus iaculis finibus vel id quam.
    Sed elit diam, mollis sed massa nec, convallis porta nibh. Fusce vehicula nunc id ex pulvinar dignissim.
    Fusce bibendum enim non imperdiet pretium. Sed tristique nunc sit amet libero egestas,
    id bibendum sem mattis. Phasellus bibendum gravida quam, a ultrices nunc congue sit amet.
    Vestibulum elementum arcu ex, vel aliquam ligula bibendum eu.
</p>

<h3>Server TeamSpeak</h3>
<p>
    Address: 1.2.3.4:9987
    <br>
    Password: 123456
</p>

<h3>Server Rules</h3>
<p>
    Forbidden:
    <br>
    1. Insulting players
    <br>
    2. Attack friendly aircraft, vehicles, buildings and etc.
</p>

<h3>Server Team</h3>
<p>
    Administrators: nickname1, nickname2
    <br>
    Designers missions: nickname1, nickname2
    <br>
    Sponsors: nickname1, nickname2
</p>
<p>
    E-mail to communicate with the server team: email@example.com
</p>
'''

info_ru = '''
<h3>Описание</h3>
<p>
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer venenatis arcu orci,
    vel feugiat nulla sagittis in. Duis varius ipsum in urna condimentum, sed vestibulum metus tincidunt.
    Proin nisl metus, mattis et ullamcorper facilisis, commodo in dolor. Quisque turpis lacus,
    gravida et dictum in, cursus id tellus. Cras vitae nunc eu tellus iaculis finibus vel id quam.
    Sed elit diam, mollis sed massa nec, convallis porta nibh. Fusce vehicula nunc id ex pulvinar dignissim.
    Fusce bibendum enim non imperdiet pretium. Sed tristique nunc sit amet libero egestas,
    id bibendum sem mattis. Phasellus bibendum gravida quam, a ultrices nunc congue sit amet.
    Vestibulum elementum arcu ex, vel aliquam ligula bibendum eu.
</p>

<h3>Сервер TeamSpeak</h3>
<p>
    Адрес: 1.2.3.4:9987
    <br>
    Пароль: 123456
</p>

<h3>Правила сервера</h3>
<p>
    Запрещено:
    <br>
    1. Оскорблять игроков
    <br>
    2. Атаковать союзные самолеты, технику, строения и т.п.
</p>

<h3>Команда сервера</h3>
<p>
    Администраторы: nickname1, nickname2
    <br>
    Дизайнеры миссий: nickname1, nickname2
    <br>
    Спонсоры: nickname1, nickname2
</p>
<p>
    E-mail для связи с командой сервера: email@example.com
</p>
'''


def default_chunks(apps, schema_editor):
    Chunk = apps.get_model('chunks', 'Chunk')
    info = Chunk.objects.get_or_create(key='info')[0]
    info.title_en = 'Information about the server'
    info.title_ru = 'Информация о сервере'
    info.title_de = 'Informationen über den server'
    info.content_en = info_en
    info.content_ru = info_ru
    info.save()


class Migration(migrations.Migration):

    dependencies = [
        ('chunks', '0004_faq_fairplay'),
    ]

    operations = [
        migrations.RunPython(default_chunks),
    ]
