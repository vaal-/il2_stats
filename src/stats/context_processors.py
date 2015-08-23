from collections import OrderedDict

from django.conf import settings

from .models import Tour


def tours(request):
    return {
        'TOURS': OrderedDict(((tour.id, tour) for tour in Tour.objects.all().order_by('-id')))
    }
