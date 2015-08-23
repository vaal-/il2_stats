# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


faq_en = '''
<p>
<b>Why statistics on the site does not coincide with the statistics in the game?</b>
</p>
<p>
Algorithms collection statistics IL2 stats differs from statistics in-game. As a consequence of these statistics will not coincide with the game.
</p>
<br>

<p>
<b>How is calculated the rating?</b>
</p>
<p>
1) calculate how many scores player earns per one life - score / (dead + capture) = SD<br>
2) calculate how many scores player earns per one hour - score / flight time = SH<br>
3) calculate rating by formula: (SD * SH * score) / 1000
</p>
<br>

<p>
<b>Why my profile is not displayed in the table of players?</b>
</p>
<p>
Statistics exclude inactive players from the overall rating. By default players inactive for more than 7 days - do not participate in the rating.
</p>
<br>

<p>
<b>I landed at the airfield, but sortie status - landing not on airfield. Why?</b>
</p>
<p>
Landing working only on active airfield. Usually active airfield is the one where you can respawn.
</p>
<br>
'''


faq_ru = '''
<p>
<b>Почему статистика на сайте не совпадает со статистикой внутри игры?</b>
</p>
<p>
Алгоритмы сбора статистики IL2 stats отличаются от статистики в игре. Как следствие данная статистика не будет совпадать с игровой.
</p>
<br>

<p>
<b>Как рассчитывается рейтинг?</b>
</p>
<p>
Рейтинг пилота рассчитывается на основе заработанных пилотом очков, среднего количества очков за жизнь и за час. Такой способ расчета рейтинга учитывает не только количественные, но и качественные показатели пилота, а так же сводит в единую систему оценки пилотов разных специализаций.<br>
Как именно рассчитывается рейтинг:<br>
1) вычисляем сколько игрок зарабатывает очков за одну жизнь - очки / (смерти + плен) = ОС<br>
2) вычисляем сколько игрок зарабатывает очков за один час налета - очки / налет часов = ОЧ<br>
3) вычисляем рейтинг по формуле: (ОС * ОЧ * очки) / 1000
</p>
<br>

<p>
<b>Почему мой профиль не отображается в общей таблице игроков?</b>
</p>
<p>
В статистике включена опция которая исключает неактивных игроков из общего рейтинга. По умолчанию игроки неактивные более 7 дней - не участвуют в рейтинге.
</p>
<br>

<p>
<b>Я приземлился на аэродром, но в статусе вылета указана посадка в поле. Почему?</b>
</p>
<p>
Посадка засчитывается только на активный аэродром. Как правило активный аэродром это тот на котором вы можете начать вылет.
</p>
<br>
'''


def default_chunks(apps, schema_editor):
    Chunk = apps.get_model('chunks', 'Chunk')
    Chunk.objects.create(
        key='server_name',
        title_en='Server name',
        title_ru='Название сервера',
        content_en='Dedicated server',
        content_ru='Выделенный сервер',
    )
    Chunk.objects.create(
        key='server_forum_url',
    )
    Chunk.objects.create(
        key='faq',
        title_en='FAQ',
        title_ru='FAQ',
        content_en=faq_en,
        content_ru=faq_ru,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('chunks', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(default_chunks),
    ]
