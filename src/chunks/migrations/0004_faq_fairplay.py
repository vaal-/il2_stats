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

<p>
<b>What is the Fairplay Index?</b>
</p>
<p>
Fairplay Index is an indicator of the correct behavior of the player, it affects the score.The maximum value - 100% indicates that the player does not violate the rules, a player receives a 100% score and all bonuses. If the index is less than 100%, that player gets a percentage of the score corresponding to the current index. Also, in this case, the player does not receive any bonuses.<br>
Violations of reducing the index:<br>
Disconnection -10%<br>
Shotdown friendly aircraft -10%<br>
Destroyed friendly ground target -5%<br>
The index recovered by 5% per flying hour, if the player did not violate the rules.<br>
The idea was borrowed from the project Bellum War.
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

<p>
<b>Что такое "Индекс честной игры"?</b>
</p>
<p>
Индекс честной игры (Fairplay) это показатель правильного поведения игрока, влияющий на получаемые им очки. Максимальное значение - 100% говорит о том, что игрок не нарушает правила, такой игрок получает 100% очков и все полагающиеся ему бонусы. Если индекс меньше 100%, то игрок получает не всю сумму заработанных очков, а лишь процент от них, соответствующий текущему индексу честной игры. Так же, в этом случае, игрок не получает ни каких бонусов.<br>
Нарушения уменьшающие индекс честной игры:<br>
Дисконнект -10%<br>
Уничтожение союзного самолета -10%<br>
Уничтожение союзной техники -5%<br>
Индекс восстанавливается по 5% за час налета, при условии игры без нарушений.<br>
Идея заимствована из проекта Bellum War.
</p>
<br>
'''


def default_chunks(apps, schema_editor):
    Chunk = apps.get_model('chunks', 'Chunk')
    faq = Chunk.objects.get_or_create(key='faq')[0]
    faq.title_en = 'FAQ'
    faq.title_ru = 'FAQ'
    faq.content_en = faq_en
    faq.content_ru = faq_ru
    faq.save()



class Migration(migrations.Migration):

    dependencies = [
        ('chunks', '0003_auto_20151107_2007'),
    ]

    operations = [
        migrations.RunPython(default_chunks),
    ]
