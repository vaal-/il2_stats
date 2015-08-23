import functools

from django.utils.translation import pgettext_lazy, ugettext_lazy as _


messages = {
    'act': {
        'damaged': pgettext_lazy('sortie_log', 'damaged'),
        'wounded': pgettext_lazy('sortie_log', 'wounded'),
        'killed': pgettext_lazy('sortie_log', 'KILLED'),
        'destroyed': pgettext_lazy('sortie_log', 'DESTROYED'),
        'shotdown': pgettext_lazy('sortie_log', 'SHOTDOWN'),

    },
    'cact': {
        'damaged': pgettext_lazy('sortie_log', 'was damaged'),
        'wounded': pgettext_lazy('sortie_log', 'was wounded'),
        'killed': pgettext_lazy('sortie_log', 'WAS KILLED'),
        'destroyed': pgettext_lazy('sortie_log', 'WAS DESTROYED'),
        'shotdown': pgettext_lazy('sortie_log', 'WAS SHOTDOWN'),
    },
}

messages_wo_opponent = {
    'act': {
        'respawn': pgettext_lazy('sortie_log', 'respawn'),
        'end': pgettext_lazy('sortie_log', 'end'),
        'takeoff': pgettext_lazy('sortie_log', 'takeoff'),
        'landed': pgettext_lazy('sortie_log', 'landed'),
        'crashed': pgettext_lazy('sortie_log', 'crashed'),
        'ditched': pgettext_lazy('sortie_log', 'ditched'),
        'bailout': pgettext_lazy('sortie_log', 'BAILOUT'),
    },
    'cact': {
        'damaged': pgettext_lazy('sortie_log', 'damage'),
        'wounded': pgettext_lazy('sortie_log', 'wound'),
        'killed': pgettext_lazy('sortie_log', 'DIED'),
        'destroyed': pgettext_lazy('sortie_log', 'DISABLED'),
        'shotdown': pgettext_lazy('sortie_log', 'DISABLED'),
    },
}


@functools.lru_cache(maxsize=64)
def get_message(act_type, event_type, has_opponent=True):
    if has_opponent:
        return messages[act_type][event_type]
    else:
        return messages_wo_opponent[act_type][event_type]


colors = {
    'act': {
        'respawn': 'grey',
        'end': 'grey',
        'takeoff': 'grey',
        'landed': 'green',
        'crashed': 'orange',
        'ditched': 'orange',
        'bailout': 'orange',

        'damaged': 'green',
        'wounded': 'green',
        'killed': 'green',
        'destroyed': 'green',
        'shotdown': 'green',
    },
    'cact': {
        'damaged': 'red',
        'wounded': 'red',
        'killed': 'red',
        'destroyed': 'red',
        'shotdown': 'red',
    },
}


@functools.lru_cache(maxsize=64)
def get_color(act_type, event_type, is_friendly_fire=False):
    if act_type == 'act' and is_friendly_fire:
        return 'black'
    return colors[act_type][event_type]
