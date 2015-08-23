from django.conf import settings as _settings

from core import __version__
from chunks.models import Chunk


def server_info(request):
    chunks = Chunk.objects.filter(key__in=('server_name', 'server_forum_url'))
    data = {chunk.key: chunk for chunk in chunks}
    data['INACTIVE_PLAYER_DAYS'] = _settings.INACTIVE_PLAYER_DAYS
    data['NEW_TOUR_BY_MONTH'] = _settings.NEW_TOUR_BY_MONTH
    data['SQUAD_MEMBERS_MINIMUM'] = _settings.SQUAD_MEMBERS_MINIMUM
    return data


def version(request):
    return {'VERSION': __version__}


def settings(request):
    return {
        'SEND_EMAIL': _settings.SEND_EMAIL,
    }
