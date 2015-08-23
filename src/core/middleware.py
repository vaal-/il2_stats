import pytz

from django.conf import settings
from django.utils import timezone


def time_zone_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        if request.user.is_authenticated and request.user.tz in pytz.common_timezones_set:
            tz = request.user.tz
        else:
            tz = settings.TIME_ZONES.get(request.LANGUAGE_CODE, settings.TIME_ZONE)
        timezone.activate(pytz.timezone(tz))

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware
