from django.core import paginator
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse


class Paginator(paginator.Paginator):
    def validate_number(self, number):
        try:
            return super().validate_number(number)
        except paginator.InvalidPage:
            raise Http404


def get_sort_by(request, sort_fields, default):
    sort_by = request.GET.get('sort_by', default)
    if sort_by.replace('-', '') not in sort_fields:
        sort_by = default
    return sort_by


def redirect_fix_url(request, param, value):
    r = request.resolver_match
    r.kwargs[param] = value
    redirect_url = '{url}?{params}'.format(
        url=reverse(viewname=r.view_name, kwargs=r.kwargs),
        params=request.META['QUERY_STRING']
    )
    return redirect(redirect_url)
