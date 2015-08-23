from django.shortcuts import redirect
from django.utils.datastructures import MultiValueDict
from django.utils.http import urlencode

from .models import Tour


def tour_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        tour_id = request.GET.get('tour')
        if tour_id:
            try:
                request.tour = Tour.objects.get(id=tour_id)
            except Tour.DoesNotExist:
                params = MultiValueDict(request.GET)
                del params['tour']
                return redirect('{url}?{params}'.format(url=request.path, params=urlencode(query=params, doseq=1)))
        else:
            try:
                request.tour = Tour.objects.get_or_create(is_ended=False)[0]
            except Tour.MultipleObjectsReturned:
                request.tour = Tour.objects.filter(is_ended=False).order_by('-id')[0]

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware
